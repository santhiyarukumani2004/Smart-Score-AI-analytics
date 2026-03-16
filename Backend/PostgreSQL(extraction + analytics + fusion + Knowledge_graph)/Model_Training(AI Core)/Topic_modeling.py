#  Topic modeling --> LDA 
# 1. LDA 
# NLP ENGINE → lda_topics.py

# Topic_modeling_LDA.py

# import psycopg2
# import pandas as pd
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.decomposition import LatentDirichletAllocation

# # ---------------- DB CONNECTION ----------------
# conn = psycopg2.connect(
#     dbname="exam_ai_db",
#     user="postgres",
#     password="password",
#     host="localhost",
#     port="5432"
# )
# cur = conn.cursor()

# # ---------------- FETCH DATA ----------------
# query = """
# SELECT t.id AS source_id, t.tweet_text, a.exam
# FROM tweets_raw t
# JOIN analytics_tweets a ON t.id = a.tweet_id
# """
# df = pd.read_sql(query, conn)

# # ---------------- VECTORIZE ----------------
# vectorizer = CountVectorizer(
#     stop_words="english",
#     max_features=1000
# )

# X = vectorizer.fit_transform(df["tweet_text"])

# # ---------------- LDA MODEL ----------------
# lda = LatentDirichletAllocation(
#     n_components=5,
#     random_state=42
# )

# topic_distributions = lda.fit_transform(X)

# # ---------------- INSERT INTO DB ----------------
# for idx, row in df.iterrows():

#     topic_id = int(topic_distributions[idx].argmax())
#     probability = float(topic_distributions[idx][topic_id])

#     cur.execute("""
#     INSERT INTO analytics_topics
#     (source, source_id, exam, topic_id, topic_label, probability, model_name)
#     VALUES (%s,%s,%s,%s,%s,%s,%s)
#     """, (
#         "tweet",
#         int(row["source_id"]),
#         row["exam"],
#         topic_id,
#         f"LDA Topic {topic_id}",
#         probability,
#         "LDA"
#     ))

# conn.commit()
# cur.close()
# conn.close()

# print("✅ LDA topics stored successfully (keywords handled separately)")


# IndicBert
# NLP ENGINE → bert_topics.py

import psycopg2
import pandas as pd
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
import numpy as np

# ---------------- DB CONNECTION ----------------
conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# ---------------- FETCH DATA ----------------
query = """
SELECT t.id AS tweet_id, t.tweet_text, a.exam
FROM tweets_raw t
JOIN analytics_tweets a ON t.id = a.tweet_id
"""
df = pd.read_sql(query, conn)

texts = df["tweet_text"].tolist()
print(f"📥 Loaded {len(texts)} tweets")

# ---------------- EMBEDDINGS ----------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedding_model.encode(
    texts,
    batch_size=16,
    show_progress_bar=True
)

# ---------------- BERTopic ----------------
topic_model = BERTopic(
    min_topic_size=10,
    calculate_probabilities=True,
    verbose=True
)

topics, probs = topic_model.fit_transform(texts, embeddings)

# ---------------- INSERT QUERY ----------------
insert_query = """
INSERT INTO analytics_topics (
    source,
    source_id,
    exam,
    topic_id,
    topic_label,
    probability,
    model_name
)
VALUES (%s,%s,%s,%s,%s,%s,%s)
"""

# ---------------- INSERT LOOP ----------------
for i, topic_id in enumerate(topics):

    # Skip noise topics
    if topic_id == -1:
        continue

    # Extract correct probability
    if probs is not None and topic_id < probs.shape[1]:
        topic_prob = float(probs[i][topic_id])
    else:
        topic_prob = None

    cur.execute(insert_query, (
        "tweet",
        int(df.iloc[i]["tweet_id"]),
        df.iloc[i]["exam"],
        int(topic_id),
        f"BERT Topic {topic_id}",
        topic_prob,
        "BERTopic"
    ))

conn.commit()
cur.close()
conn.close()

print("✅ BERTopic topics stored correctly in analytics_topics")
