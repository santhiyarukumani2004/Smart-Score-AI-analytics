import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# --------------------------------------------------
# LOAD CLEANED CSV
csv_path = r"F:\Project\Memes\memes_cleaned_FINAL.csv"

df = pd.read_csv(csv_path, dtype=str)
print("CSV loaded:", df.shape)

# Replace NaN → None (Postgres NULL)
df = df.where(pd.notnull(df), None)

# --------------------------------------------------
# DB CONNECTION
conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# --------------------------------------------------
# INSERT QUERY (NO %s HERE)
df["image_url"] = df["image_url"].fillna("UNKNOWN_IMAGE")
insert_query = """
INSERT INTO memes_raw (
    image_url,
    ocr_text,
    text_content,
    emojis,
    final_text,
    emoji_score,
    total_score,
    difficulty,
    subject,
    topics,
    is_sarcastic,
    is_stress,
    source_file
)
VALUES %s
"""

# --------------------------------------------------
# PREPARE DATA
data = [
    (
        row.get("image_url"),
        row.get("ocr_text"),
        row.get("text_content"),
        row.get("emojis"),
        row.get("final_text"),   # MUST NOT BE NULL
        row.get("emoji_score"),
        row.get("total_score"),
        row.get("difficulty"),
        row.get("subject"),
        row.get("topics"),
        row.get("is_sarcastic"),
        row.get("is_stress"),
        "memes_cleaned_FINAL.csv"
    )
    for _, row in df.iterrows()
]

# --------------------------------------------------
# BULK INSERT
execute_values(cur, insert_query, data, page_size=500)

conn.commit()
cur.close()
conn.close()

print("✅ Memes inserted successfully into memes_raw")
