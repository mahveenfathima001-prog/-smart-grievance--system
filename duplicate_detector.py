# duplicate_detector.py
# Detects duplicate/similar complaints using TF-IDF + Cosine Similarity

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import numpy as np

# Similarity threshold — complaints above this are considered duplicates
SIMILARITY_THRESHOLD = 0.65   # 65% similar = duplicate

def get_all_complaints():
    """Fetch all existing complaints from DB"""
    conn = sqlite3.connect('grievances.db')
    data = conn.execute(
        "SELECT id, title, description FROM complaints"
    ).fetchall()
    conn.close()
    return data


def check_duplicate(new_title, new_description, exclude_id=None):
    """
    Check if a new complaint is similar to existing ones.
    Returns list of similar complaints with similarity scores.
    """
    complaints = get_all_complaints()

    if not complaints:
        return []

    # Combine title + description for better matching
    new_text = (new_title + " " + new_description).lower().strip()

    # Filter out the complaint being checked (for updates)
    existing = [
        c for c in complaints
        if c[0] != exclude_id
    ]

    if not existing:
        return []

    # Build corpus
    existing_texts = [
        (str(c[1] or '') + " " + str(c[2] or '')).lower().strip()
        for c in existing
    ]

    # All texts including new one
    all_texts = existing_texts + [new_text]

    try:
        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),   # unigrams + bigrams
            min_df=1
        )
        tfidf_matrix = vectorizer.fit_transform(all_texts)

        # Cosine similarity between new text and all existing
        new_vec      = tfidf_matrix[-1]
        existing_vec = tfidf_matrix[:-1]
        similarities = cosine_similarity(new_vec, existing_vec)[0]

        # Find duplicates above threshold
        duplicates = []
        for i, score in enumerate(similarities):
            if score >= SIMILARITY_THRESHOLD:
                duplicates.append({
                    'id':          existing[i][0],
                    'title':       existing[i][1],
                    'description': existing[i][2],
                    'similarity':  round(float(score) * 100, 1)
                })

        # Sort by similarity descending
        duplicates.sort(key=lambda x: x['similarity'], reverse=True)
        return duplicates

    except Exception as e:
        print(f"⚠️ Duplicate detection error: {e}")
        return []


def get_duplicate_groups():
    """
    Find all groups of similar complaints in the DB.
    Useful for admin dashboard overview.
    """
    complaints = get_all_complaints()

    if len(complaints) < 2:
        return []

    texts = [
        (str(c[1] or '') + " " + str(c[2] or '')).lower().strip()
        for c in complaints
    ]

    try:
        vectorizer   = TfidfVectorizer(stop_words='english', ngram_range=(1,2), min_df=1)
        tfidf_matrix = vectorizer.fit_transform(texts)
        sim_matrix   = cosine_similarity(tfidf_matrix)

        visited = set()
        groups  = []

        for i in range(len(complaints)):
            if i in visited:
                continue
            group = [complaints[i]]
            visited.add(i)

            for j in range(i+1, len(complaints)):
                if j not in visited and sim_matrix[i][j] >= SIMILARITY_THRESHOLD:
                    group.append(complaints[j])
                    visited.add(j)

            if len(group) > 1:
                groups.append(group)

        return groups

    except Exception as e:
        print(f"⚠️ Error finding duplicate groups: {e}")
        return []