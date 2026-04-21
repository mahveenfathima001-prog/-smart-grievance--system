import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

# ---------------- IMPROVED TRAINING DATA ----------------
data = {
    "text": [
        # Water
        "no water supply in my area",
        "water leakage in pipeline",
        "drinking water problem",
        "tap water not coming",
        "water pipe burst",
        "low water pressure issue",

        # Electricity
        "power cut happening daily",
        "electricity not available",
        "high electricity bill issue",
        "transformer not working",
        "frequent power outage",
        "voltage fluctuation problem",

        # Sanitation
        "garbage not collected for days",
        "dirty streets full of waste",
        "drainage overflow problem",
        "bad smell from garbage",
        "waste not cleaned in area",
        "sewage system blocked",

        # Infrastructure
        "road is broken and full of potholes",
        "street lights not working",
        "bridge construction issue",
        "damaged road surface",
        "poor road condition",
        "no proper footpath in street"
    ],
    "label": [
        # Water
        "Water","Water","Water","Water","Water","Water",

        # Electricity
        "Electricity","Electricity","Electricity","Electricity","Electricity","Electricity",

        # Sanitation
        "Sanitation","Sanitation","Sanitation","Sanitation","Sanitation","Sanitation",

        # Infrastructure
        "Infrastructure","Infrastructure","Infrastructure","Infrastructure","Infrastructure","Infrastructure"
    ]
}

df = pd.DataFrame(data)

# ---------------- MODEL ----------------
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

# Train model
model.fit(df["text"], df["label"])

# Save model
joblib.dump(model, "grievance_model.pkl")

print("✅ Model trained and saved successfully!")
