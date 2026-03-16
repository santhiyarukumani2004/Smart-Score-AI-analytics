# NLP ENGINE --> analyse_memes
# NLP ENGINE → analyse_memes.py

import psycopg2
import re

conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

STRESS_WORDS = [
    "stress", "pressure", "anxiety", "panic", "fear",
    "burnout", "failure", "depression", "overwhelmed"
]

SARCASM_WORDS = [
    "yeah right", "sure", "as if", "great job",
    "wow", "nice", "legendary"
]

EMOJI_PATTERN = re.compile(
    "[\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF]+"
)

def detect_exam(text):
    t = text.lower()
    if "neet" in t: return "NEET"
    if "jee" in t: return "JEE"
    if "net" in t: return "NET"
    if "tnpsc" in t: return "TNPSC"
    return "GENERAL"

cur.execute("""
SELECT id, final_text, emojis
FROM memes_raw
WHERE final_text IS NOT NULL
""")

memes = cur.fetchall()

insert_sql = """
INSERT INTO analytics_memes
(meme_id, exam, stress_score, stress_level,
 is_stress, emoji_score, is_sarcastic, difficulty_signal)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
"""

for meme_id, text, emojis in memes:

    exam = detect_exam(text)

    stress_score = sum(
        1 for w in STRESS_WORDS
        if re.search(rf"\b{w}\b", text.lower())
    )

    stress_level = (
        "high" if stress_score >= 3 else
        "medium" if stress_score == 2 else
        "low"
    )

    is_stress = stress_score > 0

    emoji_score = len(EMOJI_PATTERN.findall(emojis or ""))

    is_sarcastic = (
        any(w in text.lower() for w in SARCASM_WORDS)
        or emoji_score >= 2
    )

    difficulty = (
        "hard" if stress_level == "high" else
        "medium" if stress_level == "medium" else
        "low"
    )

    cur.execute(insert_sql, (
        meme_id, exam, stress_score, stress_level,
        is_stress, emoji_score, is_sarcastic, difficulty
    ))

conn.commit()
cur.close()
conn.close()

print("✅ analytics_memes populated")
