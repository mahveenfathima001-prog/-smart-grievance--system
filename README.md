# 🏛️ Smart Grievance Management System
### AI-Powered Public Grievance Redressal Portal

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![ML](https://img.shields.io/badge/ML-BERT%20Zero--Shot-orange)
![NLP](https://img.shields.io/badge/NLP-Multilingual-purple)
![Languages](https://img.shields.io/badge/Supports-English%20%7C%20Telugu%20%7C%20Hindi-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Live Demo
> 🔗 [View Live Project](https://your-deployment-link.com) *(coming soon)*

---

## 💡 About This Project

I built this **Smart Grievance Management System** to solve a real problem — citizens in India struggle to report and track public complaints like broken roads, water supply issues, and power outages. Most government portals are outdated, English-only, and have no AI.

This system changes that by using **AI to automatically classify complaints, detect urgency, prevent duplicates, and notify citizens via WhatsApp** — all in their own language (English, Telugu, or Hindi).

> Built entirely from scratch using Python, Flask, and state-of-the-art NLP models.

---

## ✨ Features

### 🤖 AI & Machine Learning
- **BERT Zero-Shot Classification** — Automatically classifies complaints into 10 categories with ~90% accuracy (no training data needed)
- **Sentiment Analysis** — Detects complaint urgency (Urgent / Neutral / Positive) using NLTK VADER
- **Priority Scoring (1-10)** — AI assigns priority score based on keywords, sentiment, and category
- **Duplicate Detection** — TF-IDF + Cosine Similarity detects similar complaints automatically

### 🌐 Multilingual NLP
- Citizens can type in **English, Telugu, or Hindi**
- Auto language detection using LangDetect
- Auto translation to English for AI processing
- Original language preserved in database

### 📍 Location Intelligence
- Interactive **Leaflet.js map** for pinning complaint location
- **GPS auto-detection** — one click to use current location
- Reverse geocoding — auto fills address from map pin
- Admin sees **Google Maps link** to exact complaint location

### 📱 WhatsApp Notifications
- Citizens receive **WhatsApp notifications** via Twilio on complaint submission
- Status update notifications when admin changes complaint status
- Smart fallback — tries WhatsApp first, falls back to SMS

### 📊 Analytics & Monitoring
- Real-time **Chart.js dashboard** — bar charts, doughnut charts, trend lines
- Category-wise, sentiment-wise, language-wise breakdown
- SLA deadline tracking with overdue alerts
- Duplicate complaint grouping

### 🎨 UI/UX
- Indian Government style design (inspired by DigiLocker/UMANG)
- Navy blue + Orange color scheme
- Fully responsive — works on mobile and desktop
- Multilingual UI — headings, placeholders, buttons change language

---

## 🗂️ Project Structure

```
grievance-system/
│
├── app.py                     # Main Flask application (all routes)
├── classifier.py              # BERT Zero-Shot classifier
├── duplicate_detector.py      # TF-IDF duplicate detection
├── priority_sla.py            # Priority scoring + SLA logic
├── notification.py            # Twilio WhatsApp/SMS notifications
├── train_model.py             # Naive Bayes fallback model trainer
├── sentiment.py               # Sentiment analysis helper
│
├── templates/
│   ├── form.html              # Citizen complaint form + map
│   ├── admin.html             # Admin dashboard
│   ├── login.html             # Secure admin login
│   ├── track.html             # Public complaint tracker
│   ├── analytics.html         # Charts & analytics
│   ├── duplicate_warning.html # Duplicate complaint warning
│   └── duplicates.html        # Duplicate groups overview
│
├── static/
│   └── uploads/               # Citizen uploaded photos
│
├── grievance_model.pkl        # Trained ML model
├── requirements.txt           # Python dependencies
├── Procfile                   # Deployment config
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10, Flask 3.0 |
| **Database** | SQLite |
| **ML Model** | HuggingFace BERT (facebook/bart-large-mnli) |
| **NLP** | NLTK VADER, Scikit-learn TF-IDF |
| **Translation** | Deep Translator (Google Translate API) |
| **Language Detection** | LangDetect |
| **Maps** | Leaflet.js + OpenStreetMap + Nominatim |
| **Charts** | Chart.js |
| **Notifications** | Twilio (WhatsApp + SMS) |
| **Auth** | Flask-Login + Werkzeug |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Fonts** | Google Fonts (Noto Sans, Noto Sans Telugu, Noto Sans Devanagari) |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/mahveenfathima/smart-grievance-system.git
cd smart-grievance-system

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train the fallback model
python train_model.py

# 5. Run the app
python app.py
```

### Open in browser
```
http://127.0.0.1:5000
```

### Admin Login
```
Username: admin
Password: admin123
```

---

## 📦 requirements.txt

```txt
flask
flask-login
werkzeug
nltk
scikit-learn
pandas
joblib
langdetect
deep-translator
transformers
torch
twilio
python-dotenv
gunicorn
```

---

## 🤖 How the AI Pipeline Works

```
Citizen submits complaint (any language)
            ↓
    LangDetect → detect language
            ↓
    Deep Translator → translate to English
            ↓
    BERT Zero-Shot → classify category
    (Water / Electricity / Sanitation etc.)
            ↓
    VADER Sentiment → detect urgency
            ↓
    Priority Algorithm → score 1-10
    (keywords + sentiment + category)
            ↓
    SLA Calculator → set deadline
    (12h to 96h based on category)
            ↓
    TF-IDF Cosine Similarity → check duplicates
            ↓
    Twilio → WhatsApp notification to citizen
            ↓
    Save to SQLite database
```

---

## 📊 Supported Categories & SLA

| Category | Department | SLA Deadline |
|---------|-----------|-------------|
| ⚡ Electricity | Electricity Board | 12 hours |
| 💧 Water | Water Supply Dept | 24 hours |
| 🗑️ Sanitation | Municipality | 48 hours |
| 🚌 Transport | Transport Dept | 48 hours |
| 🛣️ Infrastructure | Public Works | 72 hours |
| 🌳 Parks & Trees | Horticulture Dept | 96 hours |
| 📢 Noise Pollution | Pollution Control | 24 hours |
| 📋 General | General Administration | 72 hours |

---

## 📱 App Pages

| Page | Route | Access |
|------|-------|--------|
| Complaint Form | `/` | Everyone |
| Track Complaint | `/track` | Everyone |
| Admin Login | `/login` | Everyone |
| Admin Dashboard | `/admin` | Admin only |
| Analytics | `/analytics` | Admin only |
| Duplicate Groups | `/duplicates` | Admin only |
| Refresh SLA | `/refresh_sla` | Admin only |

---

## 📈 What Makes This Different

| Feature | Typical Projects | This Project |
|---------|-----------------|-------------|
| Category classification | Manual dropdown | ✅ BERT AI auto-classify |
| Language support | English only | ✅ Telugu, Hindi + more |
| Location | Text only | ✅ Interactive map + GPS |
| Notifications | Email only | ✅ WhatsApp + SMS |
| Duplicate handling | None | ✅ AI similarity detection |
| Priority | Manual | ✅ AI scored 1-10 |
| SLA tracking | None | ✅ Auto deadlines + alerts |
| Analytics | None | ✅ Real-time charts |

---

## 🔒 Security

- Passwords hashed with **Werkzeug PBKDF2**
- Session management via **Flask-Login**
- File upload validation (type + size limit)
- SQL injection prevention via parameterized queries
- Protected routes with `@login_required` decorator
- Environment variables for sensitive credentials

---

## 🌍 Multilingual Support

| Language | Script | Auto-detect | Auto-translate |
|---------|--------|------------|---------------|
| English | Latin | ✅ | — |
| Telugu | తెలుగు | ✅ | ✅ |
| Hindi | हिन्दी | ✅ | ✅ |
| Tamil | தமிழ் | ✅ | ✅ |
| Kannada | ಕನ್ನಡ | ✅ | ✅ |
| Malayalam | മലയാളം | ✅ | ✅ |

---

## 🚀 Future Improvements

- [ ] Deploy on cloud (Render / Railway / AWS)
- [ ] Add voice complaint submission
- [ ] Mobile app (Flutter)
- [ ] Officer mobile app for field updates
- [ ] Real-time dashboard (WebSockets)
- [ ] PDF complaint report generation
- [ ] Complaint feedback/rating system
- [ ] Upgrade Twilio to production WhatsApp Business API

---

## 👩‍💻 About Me

Hi! I'm **Mahveen Fathima**, a B.Tech CSE(DATA SCIENCE) student from Hyderabad passionate about building real-world AI applications. I built this project to explore how ML and NLP can solve everyday civic problems in India.

- 📧 Email: mahveenfathima001@gmail.com
- 💼 LinkedIn: [linkedin.com/in/mahveenfathima](https://linkedin.com/in/mahveenfathima001)
- 🐙 GitHub: [github.com/mahveenfathima](https://github.com/mahveenfathima001)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [HuggingFace](https://huggingface.co) — BERT transformer model
- [Twilio](https://twilio.com) — WhatsApp/SMS API
- [OpenStreetMap](https://openstreetmap.org) — Map data
- [Chart.js](https://chartjs.org) — Analytics charts
- [Leaflet.js](https://leafletjs.com) — Interactive maps

---

> ⭐ **If you like this project, please give it a star on GitHub!**

> 💬 **Feel free to open issues or contribute** — PRs are welcome!
