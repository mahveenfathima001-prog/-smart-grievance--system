from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

def get_sentiment(text):
    score = sia.polarity_scores(text)

    if score['compound'] >= 0.3:
        return "Positive 😊"
    elif score['compound'] <= -0.3:
        return "Urgent 🔴"
    else:
        return "Neutral 🟡"
