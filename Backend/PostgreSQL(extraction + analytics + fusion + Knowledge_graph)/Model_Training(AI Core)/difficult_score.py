import psycopg2
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------------- DB CONNECTION ----------------
conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# ---------------- FETCH PAPERS ----------------
cur.execute("""
    SELECT id, question_text, exam, subject, topic
    FROM papers_raw
    WHERE question_text IS NOT NULL
""")

rows = cur.fetchall()
print(f"📥 Fetched {len(rows)} questions")

texts = [r[1] for r in rows]

# ---------------- TF-IDF ----------------
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=100
)
tfidf_matrix = vectorizer.fit_transform(texts)

# ---------------- ANALYSIS ----------------
insert_query = """
INSERT INTO analytics_papers (
    paper_id, exam, subject, topic,
    difficulty_predicted, difficulty_score,
    bloom_level_predicted, cognitive_load,
    keyword_density
)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

for idx, (paper_id, text, exam, subject, topic) in enumerate(rows):

    word_count = len(text.split())
    tfidf_score = tfidf_matrix[idx].sum()

    # -------- Cognitive Load --------
    if word_count > 120:
        cognitive_load = 3
    elif word_count > 70:
        cognitive_load = 2
    else:
        cognitive_load = 1

    # -------- Difficulty --------
    if cognitive_load == 3 or tfidf_score > 5:
        difficulty = "hard"
        diff_score = 0.8
    elif cognitive_load == 2:
        difficulty = "medium"
        diff_score = 0.5
    else:
        difficulty = "easy"
        diff_score = 0.2

    # -------- Bloom Level --------
    text_lower = text.lower()
    if any(k in text_lower for k in ["prove", "analyze", "justify"]):
        bloom = "analyze"
    elif any(k in text_lower for k in ["calculate", "derive", "solve"]):
        bloom = "apply"
    else:
        bloom = "remember"

    cur.execute(insert_query, (
        paper_id,
        exam,
        subject,
        topic,
        difficulty,
        diff_score,
        bloom,
        cognitive_load,
        float(tfidf_score)
    ))

# ---------------- COMMIT ----------------
conn.commit()
cur.close()
conn.close()

print("✅ analytics_papers populated successfully")


# Difficulty =
#   (Tweet Stress × Topic Weight)
# + (Meme Stress × Emotion)
# + (Paper Historical Difficulty)