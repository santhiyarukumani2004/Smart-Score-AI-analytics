# NLP ENGINE --> analyse_tweets

# NLP ENGINE → analyse_tweets.py

import psycopg2
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---------------- DB CONNECTION ----------------
conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

analyzer = SentimentIntensityAnalyzer()

STRESS_WORDS = [
    "stress", "pressure", "anxiety", "panic", "fear",
    "burnout", "tired", "sleepless", "exam fear", "overwhelmed"
]

def detect_exam(text):
    t = text.lower()
    if any(k in t for k in ["neet", "mbbs", "medical"]): return "NEET"
    if any(k in t for k in ["jee", "iit", "engineering"]): return "JEE"
    if any(k in t for k in ["ugc net", "net exam"]): return "NET"
    if any(k in t for k in ["tnpsc", "group 1", "group 2"]): return "TNPSC"
    return "GENERAL"

cur.execute("""
SELECT id, tweet_text
FROM tweets_raw
WHERE tweet_text IS NOT NULL
""")

tweets = cur.fetchall()

insert_sql = """
INSERT INTO analytics_tweets
(tweet_id, exam, sentiment_score, sentiment_label,
 stress_score, is_stress, difficulty_signal)
VALUES (%s,%s,%s,%s,%s,%s,%s)
"""

for tweet_id, text in tweets:

    exam = detect_exam(text)

    sentiment = analyzer.polarity_scores(text)
    score = sentiment["compound"]

    label = (
        "positive" if score >= 0.05 else
        "negative" if score <= -0.05 else
        "neutral"
    )

    stress_score = sum(
        1 for w in STRESS_WORDS
        if re.search(rf"\b{w}\b", text.lower())
    )

    is_stress = stress_score > 0

    difficulty = (
        "hard" if stress_score >= 3 else
        "medium" if stress_score == 2 else
        "low"
    )

    cur.execute(insert_sql, (
        tweet_id, exam, score, label,
        stress_score, is_stress, difficulty
    ))

conn.commit()
cur.close()
conn.close()

print("✅ analytics_tweets populated")
