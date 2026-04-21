# priority_sla.py
# Priority Scoring (1-10) + SLA Timer logic

from datetime import datetime, timedelta

# ============================================================
# SLA DEADLINES per category (in hours)
# ============================================================
SLA_HOURS = {
    "Water":          24,    # 1 day
    "Electricity":    12,    # 12 hours
    "Sanitation":     48,    # 2 days
    "Infrastructure": 72,    # 3 days
    "Transport":      48,    # 2 days
    "Noise Pollution":24,    # 1 day
    "Parks & Trees":  96,    # 4 days
    "General":        72,    # 3 days
}

# ============================================================
# PRIORITY KEYWORDS — higher weight = more urgent
# ============================================================
URGENT_KEYWORDS = {
    # Score 10 keywords
    "accident":       10, "fire":          10, "flood":        10,
    "collapse":       10, "emergency":     10, "death":        10,
    "electrocution":  10, "explosion":     10,

    # Score 8 keywords
    "hospital":        8, "school":         8, "children":      8,
    "no water":        8, "no electricity": 8, "days":          7,
    "weeks":           8, "dangerous":      8, "injury":        8,

    # Score 6 keywords
    "broken":          6, "blocked":        6, "overflow":      6,
    "leakage":         6, "damage":         6, "pothole":       6,
    "garbage":         5, "smell":          5, "complaint":     4,

    # Score 3 keywords
    "issue":           3, "problem":        3, "request":       2,
    "please":          2, "kindly":         2,
}

# ============================================================
# PRIORITY SCORING FUNCTION
# ============================================================
def calculate_priority(title, description, sentiment, category):
    """
    Calculate priority score (1-10) based on:
    - Sentiment (urgent = +3, neutral = +1)
    - Keywords in title/description
    - Category urgency
    Returns: score (1-10), label (Critical/High/Medium/Low)
    """
    score = 0
    text  = (title + " " + description).lower()

    # 1. Sentiment score
    if 'Urgent' in sentiment:
        score += 3
    elif 'Neutral' in sentiment:
        score += 1

    # 2. Keyword scoring
    keyword_score = 0
    for keyword, weight in URGENT_KEYWORDS.items():
        if keyword in text:
            keyword_score = max(keyword_score, weight)
    score += min(keyword_score, 5)   # cap keyword contribution at 5

    # 3. Category urgency bonus
    category_bonus = {
        "Electricity": 2,
        "Water":       2,
        "Sanitation":  1,
        "Infrastructure": 1,
    }
    score += category_bonus.get(category, 0)

    # Clamp between 1 and 10
    score = max(1, min(10, score))

    # Priority label
    if score >= 8:
        label = "Critical"
    elif score >= 6:
        label = "High"
    elif score >= 4:
        label = "Medium"
    else:
        label = "Low"

    print(f"🔢 Priority Score: {score}/10 ({label})")
    return score, label


# ============================================================
# SLA DEADLINE CALCULATOR
# ============================================================
def calculate_sla_deadline(category, created_at_str):
    """
    Calculate SLA deadline based on category.
    Returns deadline as string.
    """
    try:
        hours    = SLA_HOURS.get(category, 72)
        created  = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M")
        deadline = created + timedelta(hours=hours)
        print(f"⏱ SLA Deadline: {deadline.strftime('%Y-%m-%d %H:%M')} ({hours}hrs)")
        return deadline.strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        print(f"⚠️ SLA calculation error: {e}")
        return None


# ============================================================
# SLA STATUS CHECKER
# ============================================================
def check_sla_status(sla_deadline_str, current_status):
    """
    Check if complaint is within SLA, overdue, or resolved.
    Returns: 'Resolved', 'Overdue', 'Due Soon', 'On Time'
    """
    if current_status == 'Resolved':
        return 'Resolved ✅'

    if not sla_deadline_str:
        return 'On Time'

    try:
        deadline = datetime.strptime(sla_deadline_str, "%Y-%m-%d %H:%M")
        now      = datetime.now()
        diff     = deadline - now

        if now > deadline:
            return 'Overdue ❌'
        elif diff.total_seconds() < 3600 * 6:   # less than 6 hours
            return 'Due Soon ⚠️'
        else:
            return 'On Time ✅'

    except Exception as e:
        print(f"⚠️ SLA status error: {e}")
        return 'On Time'


# ============================================================
# TIME REMAINING FORMATTER
# ============================================================
def time_remaining(sla_deadline_str, current_status):
    """
    Returns human-readable time remaining or overdue time.
    """
    if current_status == 'Resolved':
        return '✅ Resolved'

    if not sla_deadline_str:
        return 'N/A'

    try:
        deadline = datetime.strptime(sla_deadline_str, "%Y-%m-%d %H:%M")
        now      = datetime.now()
        diff     = deadline - now

        if now > deadline:
            overdue = now - deadline
            hours   = int(overdue.total_seconds() // 3600)
            mins    = int((overdue.total_seconds() % 3600) // 60)
            return f"Overdue by {hours}h {mins}m"
        else:
            hours = int(diff.total_seconds() // 3600)
            mins  = int((diff.total_seconds() % 3600) // 60)
            return f"{hours}h {mins}m remaining"

    except Exception as e:
        return 'N/A'