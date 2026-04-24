from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from langdetect import detect
from deep_translator import GoogleTranslator
from datetime import datetime
import sqlite3
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import os
import uuid
import json
import traceback

# ============================================================
# STEP 1 — CREATE APP
# ============================================================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "grievance2024secretkey")

# ============================================================
# STEP 2 — CONFIGURE APP
# ============================================================
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================
# STEP 3 — FLASK-LOGIN SETUP
# ============================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

ADMIN_USERNAME      = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ============================================================
# STEP 4 — SENTIMENT SETUP
# ============================================================
nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

# ============================================================
# STEP 5 — BERT CLASSIFIER
# ============================================================

# ✅ Always define these first so they exist even if BERT loads
old_model    = None
model_loaded = False

try:
    from classifier import classify_with_confidence, classify_grievance
    bert_loaded = True
    print("✅ BERT Zero-Shot Classifier ready!")
except Exception as e:
    bert_loaded = False
    print(f"⚠️ BERT not loaded: {e}")

if not bert_loaded:
    import joblib
    MODEL_PATH = "grievance_model.pkl"
    if os.path.exists(MODEL_PATH):
        old_model    = joblib.load(MODEL_PATH)
        model_loaded = True
        print("✅ Naive Bayes fallback loaded!")
    else:
        old_model    = None
        model_loaded = False
        print("⚠️ No model found!")

# ============================================================
# STEP 6 — NOTIFICATIONS
# ============================================================
try:
    from notifications import (
        notify_citizen,
        complaint_submitted_msg,
        status_updated_msg
    )
    notifications_enabled = True
    print("✅ Notifications ready!")
except Exception as e:
    notifications_enabled = False
    print(f"⚠️ Notifications disabled: {e}")
    traceback.print_exc()

# ============================================================
# STEP 7 — DUPLICATE DETECTION
# ============================================================
try:
    from duplicate_detector import check_duplicate, get_duplicate_groups
    duplicate_detection_enabled = True
    print("✅ Duplicate Detection ready!")
except Exception as e:
    duplicate_detection_enabled = False
    print(f"⚠️ Duplicate detection disabled: {e}")

# ============================================================
# STEP 8 — PRIORITY SCORING + SLA
# ============================================================
try:
    from priority_sla import (
        calculate_priority,
        calculate_sla_deadline,
        check_sla_status,
        time_remaining
    )
    priority_sla_enabled = True
    print("✅ Priority Scoring + SLA ready!")
except Exception as e:
    priority_sla_enabled = False
    print(f"⚠️ Priority/SLA disabled: {e}")

# ============================================================
# STEP 9 — HELPER FUNCTIONS
# ============================================================
def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_department(category):
    mapping = {
        "Water":          "Water Supply Department",
        "Electricity":    "Electricity Board",
        "Sanitation":     "Municipality / Cleaning Dept",
        "Infrastructure": "Public Works Department",
        "Transport":      "Transport Department",
        "Noise Pollution":"Pollution Control Board",
        "Parks & Trees":  "Horticulture Department",
        "General":        "General Administration"
    }
    return mapping.get(category, "General Administration")


def detect_and_translate(text):
    try:
        lang = detect(text)
        lang_names = {
            'te': 'Telugu', 'hi': 'Hindi',
            'en': 'English', 'ur': 'Urdu',
            'ta': 'Tamil',  'kn': 'Kannada',
            'ml': 'Malayalam', 'mr': 'Marathi',
            'bn': 'Bengali',
        }
        lang_name = lang_names.get(lang, lang.upper())
        if lang != 'en':
            english_text = GoogleTranslator(
                source=lang, target='en'
            ).translate(text)
            print(f"Detected: {lang_name} | Translated: {english_text}")
        else:
            english_text = text
            print(f"Language: English")
        return english_text, lang_name
    except Exception as e:
        print(f"Language detection failed: {e}")
        return text, "Unknown"


def predict_category(text):
    if bert_loaded:
        try:
            result     = classify_with_confidence(text)
            category   = result['category']
            confidence = result['confidence']
            print(f"BERT: {category} ({confidence}%)")
            return category, confidence
        except Exception as e:
            print(f"BERT failed: {e}")

    if model_loaded and old_model:
        category = old_model.predict([text])[0]
        print(f"Naive Bayes: {category}")
        return category, None

    return "General", None

# ============================================================
# STEP 10 — DATABASE INIT
# ============================================================
def init_db():
    conn = sqlite3.connect('grievances.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            title          TEXT,
            description    TEXT,
            category       TEXT,
            contact        TEXT,
            sentiment      TEXT,
            image          TEXT,
            language       TEXT,
            status         TEXT DEFAULT 'Pending',
            created_at     TEXT,
            address        TEXT,
            latitude       TEXT,
            longitude      TEXT,
            is_duplicate   INTEGER DEFAULT 0,
            duplicate_of   INTEGER DEFAULT NULL,
            priority_score INTEGER DEFAULT 0,
            priority_label TEXT    DEFAULT 'Low',
            sla_deadline   TEXT,
            sla_status     TEXT    DEFAULT 'On Time'
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database ready!")

# ============================================================
# STEP 11 — ROUTES
# ============================================================

# --- Home ---
@app.route('/')
def home():
    return render_template('form.html')


# --- Submit ---
@app.route('/submit', methods=['POST'])
def submit():
    title       = request.form['title']
    description = request.form['description']
    contact     = request.form['contact']
    address     = request.form.get('address', '')
    latitude    = request.form.get('latitude', '')
    longitude   = request.form.get('longitude', '')
    full_text   = title + " " + description

    print(f"\n{'='*50}")
    print(f"New complaint: {title}")
    print(f"Contact: {contact}")
    print(f"{'='*50}")

    # Detect language & translate
    english_text, detected_language = detect_and_translate(full_text)

    # Sentiment
    score = sia.polarity_scores(english_text)
    if score['compound'] >= 0.3:
        sentiment = "Positive"
    elif score['compound'] <= -0.3:
        sentiment = "Urgent"
    else:
        sentiment = "Neutral"
    print(f"Sentiment: {sentiment}")

    # Category
    category, confidence = predict_category(english_text)
    department           = get_department(category)
    print(f"Category: {category} | Dept: {department}")

    # Duplicate detection
    is_duplicate = 0
    duplicate_of = None
    duplicates   = []
    if duplicate_detection_enabled:
        duplicates = check_duplicate(title, description)
        if duplicates:
            is_duplicate = 1
            duplicate_of = duplicates[0]['id']
            print(f"Duplicate! Similar to #{duplicate_of}")

    # Image upload
    image_filename = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            ext         = file.filename.rsplit(".", 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(
                app.config["UPLOAD_FOLDER"], unique_name
            ))
            image_filename = unique_name
            print(f"Image saved: {unique_name}")

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    status     = "Pending"

    # Priority Score + SLA
    priority_score = 0
    priority_label = "Low"
    sla_deadline   = None
    sla_status_val = "On Time"

    if priority_sla_enabled:
        priority_score, priority_label = calculate_priority(
            title, description, sentiment, category
        )
        sla_deadline   = calculate_sla_deadline(category, created_at)
        sla_status_val = check_sla_status(sla_deadline, status)
        print(f"Priority: {priority_score}/10 ({priority_label})")
        print(f"SLA Deadline: {sla_deadline}")

    # Save to DB
    conn   = sqlite3.connect('grievances.db')
    cursor = conn.execute(
        """INSERT INTO complaints
           (title, description, category, contact, sentiment, image,
            language, status, created_at, address, latitude, longitude,
            is_duplicate, duplicate_of, priority_score, priority_label,
            sla_deadline, sla_status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (title, description, category, contact, sentiment,
         image_filename, detected_language, status, created_at,
         address, latitude, longitude, is_duplicate, duplicate_of,
         priority_score, priority_label, sla_deadline, sla_status_val)
    )
    complaint_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"Saved to DB: #{complaint_id}")

    # Send WhatsApp notification
    print(f"\nNotification check:")
    print(f"   notifications_enabled = {notifications_enabled}")
    print(f"   contact = '{contact}'")

    if notifications_enabled and contact:
        print("Sending WhatsApp notification...")
        try:
            message = complaint_submitted_msg(
                complaint_id, category, department
            )
            notify_citizen(contact, "Complaint Submitted", message)
        except Exception as e:
            print(f"Notification error: {e}")
            traceback.print_exc()
    else:
        if not notifications_enabled:
            print("Skipped — notifications disabled!")
        if not contact:
            print("Skipped — no contact number!")

    print(f"{'='*50}\n")

    # Show duplicate warning if found
    if duplicates:
        return render_template(
            'duplicate_warning.html',
            complaint_id = complaint_id,
            duplicates   = duplicates[:3],
            title        = title
        )

    return redirect('/')


# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and \
           check_password_hash(ADMIN_PASSWORD_HASH, password):
            login_user(User(id=1))
            print("Admin logged in")
            return redirect(url_for('admin'))
        else:
            flash("Invalid username or password!")
            print("Failed login attempt")
    return render_template('login.html')


# --- Logout ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# --- Admin dashboard ---
@app.route('/admin')
@login_required
def admin():
    conn = sqlite3.connect('grievances.db')
    data = conn.execute(
        "SELECT * FROM complaints ORDER BY priority_score DESC, id DESC"
    ).fetchall()
    conn.close()
    return render_template('admin.html', complaints=data)


# --- Update status ---
@app.route('/update_status/<int:complaint_id>', methods=['POST'])
@login_required
def update_status(complaint_id):
    new_status = request.form['status']

    conn      = sqlite3.connect('grievances.db')
    complaint = conn.execute(
        "SELECT title, contact, sla_deadline FROM complaints WHERE id = ?",
        (complaint_id,)
    ).fetchone()

    new_sla = check_sla_status(
        complaint[2], new_status
    ) if priority_sla_enabled and complaint else "On Time"

    conn.execute(
        "UPDATE complaints SET status = ?, sla_status = ? WHERE id = ?",
        (new_status, new_sla, complaint_id)
    )
    conn.commit()
    conn.close()

    print(f"Complaint #{complaint_id} updated to {new_status}")

    # Notify citizen
    if notifications_enabled and complaint:
        print(f"Sending status update to {complaint[1]}...")
        try:
            message = status_updated_msg(
                complaint_id, new_status, complaint[0]
            )
            notify_citizen(complaint[1], "Status Update", message)
        except Exception as e:
            print(f"Notification error: {e}")
            traceback.print_exc()

    return redirect(url_for('admin'))


# --- Track complaint ---
@app.route('/track', methods=['GET', 'POST'])
def track():
    complaint = None
    error     = None
    if request.method == 'POST':
        complaint_id = request.form['complaint_id']
        conn         = sqlite3.connect('grievances.db')
        complaint    = conn.execute(
            "SELECT * FROM complaints WHERE id = ?",
            (complaint_id,)
        ).fetchone()
        conn.close()
        if not complaint:
            error = f"No complaint found with ID: {complaint_id}"
    return render_template('track.html', complaint=complaint, error=error)


# --- Analytics ---
@app.route('/analytics')
@login_required
def analytics():
    conn = sqlite3.connect('grievances.db')

    total      = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    categories = conn.execute("SELECT category, COUNT(*) FROM complaints GROUP BY category").fetchall()
    sentiments = conn.execute("SELECT sentiment, COUNT(*) FROM complaints GROUP BY sentiment").fetchall()
    statuses   = conn.execute("SELECT status,   COUNT(*) FROM complaints GROUP BY status").fetchall()
    languages  = conn.execute("SELECT language, COUNT(*) FROM complaints GROUP BY language").fetchall()
    daily      = conn.execute("""
        SELECT DATE(created_at) as day, COUNT(*)
        FROM complaints WHERE created_at IS NOT NULL
        GROUP BY day ORDER BY day DESC LIMIT 7
    """).fetchall()

    conn.close()

    return render_template('analytics.html',
        total        = total,
        cat_labels   = json.dumps([r[0] or 'Unknown' for r in categories]),
        cat_data     = json.dumps([r[1] for r in categories]),
        sent_labels  = json.dumps([r[0] or 'Unknown' for r in sentiments]),
        sent_data    = json.dumps([r[1] for r in sentiments]),
        stat_labels  = json.dumps([r[0] or 'Pending'  for r in statuses]),
        stat_data    = json.dumps([r[1] for r in statuses]),
        lang_labels  = json.dumps([r[0] or 'Unknown'  for r in languages]),
        lang_data    = json.dumps([r[1] for r in languages]),
        daily_labels = json.dumps([r[0] for r in reversed(daily)]),
        daily_data   = json.dumps([r[1] for r in reversed(daily)]),
    )


# --- Duplicates ---
@app.route('/duplicates')
@login_required
def duplicates():
    groups = get_duplicate_groups() if duplicate_detection_enabled else []
    return render_template('duplicates.html', groups=groups)


# --- Refresh SLA ---
@app.route('/refresh_sla')
@login_required
def refresh_sla():
    if priority_sla_enabled:
        conn       = sqlite3.connect('grievances.db')
        complaints = conn.execute(
            "SELECT id, sla_deadline, status FROM complaints"
        ).fetchall()
        for c in complaints:
            new_sla = check_sla_status(c[1], c[2])
            conn.execute(
                "UPDATE complaints SET sla_status = ? WHERE id = ?",
                (new_sla, c[0])
            )
        conn.commit()
        conn.close()
        print("SLA statuses refreshed!")
    return redirect(url_for('admin'))


# --- Debug ---
@app.route('/debug')
def debug():
    conn = sqlite3.connect('grievances.db')
    data = conn.execute("SELECT * FROM complaints").fetchall()
    conn.close()
    return str(data)


# --- File too large ---
@app.errorhandler(413)
def too_large(e):
    return "File too large! Maximum size is 5MB.", 413


# ============================================================
# STEP 12 — RUN
# ============================================================
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
