import psycopg2
import re

# ---------------- DB CONNECTION ----------------
conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# ---------------- YEAR REGEX ----------------
YEAR_PATTERN = re.compile(r"\b(2020|2021|2022|2023|2024|2025|2026)\b")

# ---------------- FETCH TWEETS ----------------
cur.execute("""
SELECT
    a.id AS analytics_id,
    t.tweet_text,
    t.year
FROM analytics_tweets a
JOIN tweets_raw t ON a.tweet_id = t.id
WHERE a.year IS NULL
""")

rows = cur.fetchall()
print(f"📥 Found {len(rows)} analytics rows with missing year")

updated = 0

# ---------------- UPDATE LOOP ----------------
for analytics_id, tweet_text, raw_year in rows:

    final_year = None

    # 1️⃣ Use tweets_raw.year if valid
    if raw_year and str(raw_year).isdigit():
        final_year = int(raw_year)

    # 2️⃣ Extract year from tweet_text
    elif tweet_text:
        match = YEAR_PATTERN.search(tweet_text)
        if match:
            final_year = int(match.group())

    # 3️⃣ Update only if year found
    if final_year:
        cur.execute("""
        UPDATE analytics_tweets
        SET year = %s
        WHERE id = %s
        """, (final_year, analytics_id))
        updated += 1

conn.commit()
cur.close()
conn.close()

print("=================================")
print(f"✅ SUCCESS: Year updated for {updated} analytics_tweets rows")
