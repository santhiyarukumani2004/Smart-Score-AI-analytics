# NLP ENGINE → tfidf_keywords extraction 

import psycopg2
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)

df = pd.read_sql("""
SELECT t.id, t.tweet_text, a.exam
FROM tweets_raw t
JOIN analytics_tweets a ON t.id = a.tweet_id
""", conn)

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=50,
    ngram_range=(1,2)
)

X = vectorizer.fit_transform(df["tweet_text"])
features = vectorizer.get_feature_names_out()

cur = conn.cursor()

for row_idx, row in df.iterrows():
    scores = X[row_idx].toarray()[0]
    for col_idx, score in enumerate(scores):
        if score > 0:
            cur.execute("""
            INSERT INTO analytics_keywords
            (source, source_id, exam, keyword, tfidf_score)
            VALUES ('tweet', %s, %s, %s, %s)
            """, (
                int(row["id"]),
                row["exam"],
                features[col_idx],
                float(score)
            ))

conn.commit()
cur.close()
conn.close()

print("✅ TF-IDF keywords stored")
