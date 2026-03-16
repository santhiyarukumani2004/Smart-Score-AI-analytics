import psycopg2

conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

cur.execute("""
SELECT
    t.exam,
    p.year,
    AVG(t.stress_score) AS tweet_avg,
    AVG(m.stress_score) AS meme_avg,
    AVG(
        CASE
            WHEN p.difficulty='easy' THEN 0.3
            WHEN p.difficulty='medium' THEN 0.6
            WHEN p.difficulty='hard' THEN 0.9
        END
    ) AS paper_avg
FROM analytics_tweets t
JOIN analytics_memes m ON t.exam = m.exam
JOIN papers_raw p ON p.exam = t.exam
GROUP BY t.exam, p.year
""")

rows = cur.fetchall()

for exam, year, tweet_avg, meme_avg, paper_avg in rows:

    # ✅ FIX: Convert Decimal → float safely
    tweet_avg = float(tweet_avg) if tweet_avg is not None else 0.0
    meme_avg = float(meme_avg) if meme_avg is not None else 0.0
    paper_avg = float(paper_avg) if paper_avg is not None else 0.0

    # ✅ Multimodal Fusion
    fused_score = (
        tweet_avg * 0.3 +
        meme_avg * 0.3 +
        paper_avg * 0.4
    )

    # ✅ Difficulty Label
    if fused_score >= 0.75:
        label = "Hard"
    elif fused_score >= 0.45:
        label = "Medium"
    else:
        label = "Easy"

    cur.execute("""
    INSERT INTO analytics_fusion
    (exam, year,
     tweet_stress_avg, meme_stress_avg, paper_difficulty_avg,
     fused_difficulty_score, difficulty_label)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        exam, year,
        tweet_avg, meme_avg, paper_avg,
        fused_score, label
    ))

conn.commit()
cur.close()
conn.close()

print("✅ SUCCESS: Multimodal difficulty fusion completed")
