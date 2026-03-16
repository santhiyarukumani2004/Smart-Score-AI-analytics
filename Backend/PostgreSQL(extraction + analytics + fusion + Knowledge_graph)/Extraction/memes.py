import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch

# --------------------------------------------------
# 1️⃣ Load cleaned CSV (FORCE TEXT)
df = pd.read_csv(
    r"F:\Project\Memes\memes_cleaned_FINAL.csv",
    dtype=str
)

# Replace NaN → None (Postgres NULL)
df = df.where(pd.notnull(df), None)

# --------------------------------------------------
# 2️⃣ Ensure final_text is NEVER NULL
df['final_text'] = (
    df.get('ocr_text', '').fillna('') + ' ' +
    df.get('text_content', '').fillna('') + ' ' +
    df.get('emojis', '').fillna('')
).str.strip()

# Drop rows still empty (safety)
df = df[df['final_text'] != ""]

# --------------------------------------------------
# 3️⃣ Convert numeric columns safely
for col in ['emoji_score', 'total_score']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert booleans
for col in ['is_sarcastic', 'is_stress']:
    if col in df.columns:
        df[col] = df[col].map({'1': True, '0': False, 1: True, 0: False})

# --------------------------------------------------
# 4️⃣ Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# --------------------------------------------------
# 5️⃣ INSERT QUERY
insert_query = """
INSERT INTO memes_raw (
    image_url, ocr_text, text_content, emojis,
    final_text, emoji_score, total_score,
    difficulty, topics,
    is_sarcastic, is_stress,
    source_file
)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

data = [
    (
        row.get('image_url'),
        row.get('ocr_text'),
        row.get('text_content'),
        row.get('emojis'),
        row.get('final_text'),
        row.get('emoji_score'),
        row.get('total_score'),
        row.get('difficulty'),
        row.get('topics'),
        row.get('is_sarcastic'),
        row.get('is_stress'),
        row.get('source_file')
    )
    for _, row in df.iterrows()
]

# --------------------------------------------------
# 6️⃣ Batch insert (FAST & SAFE)
execute_batch(cur, insert_query, data, page_size=500)

conn.commit()
cur.close()
conn.close()

print("✅ Memes inserted successfully into memes_raw")
print(f"📊 Total records inserted: {len(data)}")
