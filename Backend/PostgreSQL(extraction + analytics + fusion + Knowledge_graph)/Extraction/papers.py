import pandas as pd
import glob
import psycopg2
from psycopg2.extras import execute_batch

# ------------------------------------------------------------
# STEP 0: LOAD ALL CSV FILES
csv_path = r"F:\Project\past_papers\*.csv"
files = glob.glob(csv_path)

if not files:
    raise FileNotFoundError("❌ No CSV files found in past_papers folder")

df_list = [pd.read_csv(f, dtype=str) for f in files]
papers_df = pd.concat(df_list, ignore_index=True)

print("✅ CSV Loaded")
print("Total rows:", len(papers_df))

# ------------------------------------------------------------
# STEP 1: BASIC CLEANING
papers_df = papers_df.where(pd.notnull(papers_df), None)

# Ensure mandatory column
papers_df = papers_df.dropna(subset=["question_text"])

# Create question_length if missing
if "question_length" not in papers_df.columns:
    papers_df["question_length"] = papers_df["question_text"].astype(str).str.len()

# Remove duplicates (same question)
papers_df = papers_df.drop_duplicates(subset=["question_text"])

print("Rows after cleaning:", len(papers_df))

# ------------------------------------------------------------
# STEP 2: CONNECT TO POSTGRES
conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# ------------------------------------------------------------
# STEP 3: INSERT QUERY
insert_query = """
INSERT INTO papers_raw (
    question_text,
    exam,
    year,
    subject,
    topic,
    bloom_level,
    difficulty,
    question_length,
    paper,
    paper_code
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

data = [
    (
        row.get("question_text"),
        row.get("exam"),
        row.get("year"),
        row.get("subject"),
        row.get("topic"),
        row.get("bloom_level"),
        row.get("difficulty"),
        int(row["question_length"]) if row.get("question_length") else None,
        row.get("paper"),
        row.get("paper_code")
    )
    for _, row in papers_df.iterrows()
]

# ------------------------------------------------------------
# STEP 4: BULK INSERT
execute_batch(cur, insert_query, data, page_size=500)

conn.commit()
cur.close()
conn.close()

print("✅ Papers inserted successfully into papers_raw")
