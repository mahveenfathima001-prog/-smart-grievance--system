# classifier.py
# Zero-Shot Classification using BERT
# No training data needed!

from transformers import pipeline
import os

print("🔄 Loading BERT model... (first time takes 1-2 minutes)")

# Load zero-shot classification pipeline
# This downloads ~1.5GB model on first run
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=-1   # -1 = CPU, 0 = GPU if available
)

print("✅ BERT model loaded successfully!")

# ---- Categories your system supports ----
CATEGORIES = [
    "Water supply problem",
    "Electricity and power issue",
    "Sanitation and garbage problem",
    "Road and infrastructure damage",
    "Street light not working",
    "Drainage and sewage problem",
    "Public transport issue",
    "Noise pollution complaint",
    "Tree and park maintenance",
    "General administration"
]

# Simplified category names for DB storage
CATEGORY_MAP = {
    "Water supply problem":          "Water",
    "Electricity and power issue":   "Electricity",
    "Sanitation and garbage problem":"Sanitation",
    "Road and infrastructure damage":"Infrastructure",
    "Street light not working":      "Infrastructure",
    "Drainage and sewage problem":   "Sanitation",
    "Public transport issue":        "Transport",
    "Noise pollution complaint":     "Noise Pollution",
    "Tree and park maintenance":     "Parks & Trees",
    "General administration":        "General"
}

def classify_grievance(text):
    """
    Classify a grievance text into a category
    using zero-shot BERT classification.
    Returns simplified category name.
    """
    try:
        result = classifier(
            text,
            candidate_labels=CATEGORIES,
            multi_label=False
        )

        # Top predicted label
        top_label = result['labels'][0]
        top_score = result['scores'][0]

        print(f"🤖 BERT Classification:")
        print(f"   Text:     {text[:60]}...")
        print(f"   Category: {top_label}")
        print(f"   Score:    {top_score:.2%}")

        # Return simplified name
        return CATEGORY_MAP.get(top_label, "General")

    except Exception as e:
        print(f"⚠️ BERT classification failed: {e}")
        return "General"


def classify_with_confidence(text):
    """
    Returns category + confidence score + all scores.
    Useful for priority scoring later.
    """
    try:
        result = classifier(
            text,
            candidate_labels=CATEGORIES,
            multi_label=False
        )

        top_label = result['labels'][0]
        top_score = result['scores'][0]
        category  = CATEGORY_MAP.get(top_label, "General")

        return {
            "category":   category,
            "confidence": round(top_score * 100, 1),
            "all_scores": dict(zip(result['labels'], result['scores']))
        }

    except Exception as e:
        print(f"⚠️ Error: {e}")
        return {"category": "General", "confidence": 0, "all_scores": {}}
# Add this to classifier.py after imports
import torch

# Use GPU if available
DEVICE = 0 if torch.cuda.is_available() else -1
print(f"🖥️ Using: {'GPU ✅' if DEVICE == 0 else 'CPU'}")

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=DEVICE
)
# In classifier.py — add at the bottom
import joblib

OLD_MODEL_PATH = "grievance_model.pkl"

def classify_with_fallback(text):
    """
    Try BERT first, fall back to Naive Bayes if needed
    """
    try:
        return classify_grievance(text)
    except Exception as e:
        print(f"⚠️ BERT failed, using old model: {e}")
        if os.path.exists(OLD_MODEL_PATH):
            old_model = joblib.load(OLD_MODEL_PATH)
            return old_model.predict([text])[0]
        return "General"