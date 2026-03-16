import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="exam_ai_db",
    user="postgres",
    password="password"
)

cur = conn.cursor()

# ---------------------------------
# Get all exams
# ---------------------------------

cur.execute("""
SELECT DISTINCT exam FROM (
    SELECT exam FROM knowledgegraph
    UNION
    SELECT exam FROM kg_tnpsc
) t
""")

exams = [row[0] for row in cur.fetchall()]

print("Found Exams:", exams)


# ---------------------------------
# Process each exam
# ---------------------------------

for exam in exams:

    print(f"\nProcessing {exam}")

    query = """
        SELECT
            COUNT(*) as topic_count,
            COALESCE(SUM(tweet_count),0) as tweet_count,

            AVG(tweet_stress_avg) as avg_stress,
            AVG(paper_difficulty_avg) as avg_difficulty,

            SUM(CASE WHEN tweet_stress_avg >= 3.5 THEN 1 ELSE 0 END) AS high,
            SUM(CASE WHEN tweet_stress_avg >= 2 AND tweet_stress_avg < 3.5 THEN 1 ELSE 0 END) AS medium,
            SUM(CASE WHEN tweet_stress_avg < 2 THEN 1 ELSE 0 END) AS low,

            SUM(CASE WHEN tweet_sentiment_label='positive' THEN 1 ELSE 0 END) as positive,
            SUM(CASE WHEN tweet_sentiment_label='negative' THEN 1 ELSE 0 END) as negative,
            SUM(CASE WHEN tweet_sentiment_label='neutral' THEN 1 ELSE 0 END) as neutral

        FROM (
                SELECT
                    exam,
                    tweet_count,
                    tweet_stress_avg,
                    tweet_sentiment_label,
                    paper_difficulty_avg
                FROM knowledgegraph
                WHERE UPPER(exam)=UPPER(%s)

                UNION ALL

                SELECT
                    exam,
                    tweet_count,
                    tweet_stress_avg,
                    tweet_sentiment_label,
                    paper_difficulty_avg
                FROM kg_tnpsc
                WHERE UPPER(exam)=UPPER(%s)

        ) data
        """

    cur.execute(query, (exam, exam))
    result = cur.fetchone()

    if not result:
        continue

    topic_count = result[0] or 0
    tweet_count = result[1] or 0
    avg_stress = result[2] or 0
    avg_difficulty = result[3] or 0

    high = result[4] or 0
    medium = result[5] or 0
    low = result[6] or 0

    positive = result[7] or 0
    negative = result[8] or 0
    neutral = result[9] or 0

    total = topic_count if topic_count else 1

    high_pct = round(high / total * 100, 2)
    medium_pct = round(medium / total * 100, 2)
    low_pct = round(low / total * 100, 2)

    pos_pct = round(positive / total * 100, 2)
    neg_pct = round(negative / total * 100, 2)
    neu_pct = round(neutral / total * 100, 2)

    insert_query = """
    INSERT INTO analytics_tweets_exam (
        exam,
        tweet_count,
        overall_stress,

        high_stress,
        medium_stress,
        low_stress,

        high_stress_pct,
        medium_stress_pct,
        low_stress_pct,

        positive_sentiment,
        negative_sentiment,
        neutral_sentiment,

        positive_pct,
        negative_pct,
        neutral_pct,

        avg_difficulty,
        topic_count
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (exam) DO UPDATE SET
        tweet_count = EXCLUDED.tweet_count,
        overall_stress = EXCLUDED.overall_stress,
        high_stress = EXCLUDED.high_stress,
        medium_stress = EXCLUDED.medium_stress,
        low_stress = EXCLUDED.low_stress,
        high_stress_pct = EXCLUDED.high_stress_pct,
        medium_stress_pct = EXCLUDED.medium_stress_pct,
        low_stress_pct = EXCLUDED.low_stress_pct,
        positive_sentiment = EXCLUDED.positive_sentiment,
        negative_sentiment = EXCLUDED.negative_sentiment,
        neutral_sentiment = EXCLUDED.neutral_sentiment,
        positive_pct = EXCLUDED.positive_pct,
        negative_pct = EXCLUDED.negative_pct,
        neutral_pct = EXCLUDED.neutral_pct,
        avg_difficulty = EXCLUDED.avg_difficulty,
        topic_count = EXCLUDED.topic_count
    """

    cur.execute(insert_query, (
        exam,
        tweet_count,
        avg_stress,

        high,
        medium,
        low,

        high_pct,
        medium_pct,
        low_pct,

        positive,
        negative,
        neutral,

        pos_pct,
        neg_pct,
        neu_pct,

        avg_difficulty,
        topic_count
    ))

    conn.commit()

    print(f"Inserted analytics for {exam}")

cur.close()
conn.close()

print("\nAll exams processed successfully")