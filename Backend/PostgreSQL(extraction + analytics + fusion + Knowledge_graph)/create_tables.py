import psycopg2

conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# 1. Raw Tables
cur.execute("""
CREATE TABLE IF NOT EXISTS tweets_raw (
    id SERIAL PRIMARY KEY,
    tweet_text TEXT NOT NULL,
    platform TEXT,
    subject TEXT,
    topic TEXT,
    year TEXT,
    source TEXT,
    link TEXT,
    source_file TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS memes_raw (
    id SERIAL PRIMARY KEY,
    image_url TEXT NOT NULL,
    ocr_text TEXT,
    text_content TEXT,
    emojis TEXT,
    final_text TEXT NOT NULL,
    emoji_score INT,
    total_score INT,
    difficulty TEXT,
    topics TEXT,
    is_sarcastic BOOLEAN,
    is_stress BOOLEAN,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT
);""")

cur.execute("""
CREATE TABLE IF NOT EXISTS papers_raw (
    id SERIAL PRIMARY KEY,
    exam TEXT,
    year INT,
    shift TEXT,
    question_text TEXT NOT NULL,
    question_length INT,
    subject TEXT,
    topic TEXT,
    bloom_level TEXT,
    difficulty TEXT
);
""")

# 2. Analytics Tables
cur.execute("""CREATE TABLE analytics_tweets (
    id SERIAL PRIMARY KEY,
    tweet_id INT REFERENCES tweets_raw(id) ON DELETE CASCADE,
    exam TEXT NOT NULL,
    sentiment_score FLOAT,
    sentiment_label TEXT,
    stress_score INT,
    is_stress BOOLEAN,
    difficulty_signal TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""CREATE TABLE analytics_memes (
    id SERIAL PRIMARY KEY,
    meme_id INT REFERENCES memes_raw(id) ON DELETE CASCADE,
    exam TEXT,
    stress_score INT,
    stress_level TEXT,
    is_stress BOOLEAN,
    emoji_score INT,
    is_sarcastic BOOLEAN,
    difficulty_signal TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""CREATE TABLE analytics_keywords (
    id SERIAL PRIMARY KEY,
    source TEXT,
    source_id INT,
    exam TEXT,
    keyword TEXT,
    tfidf_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")

cur.execute("""CREATE TABLE analytics_topics (
    id SERIAL PRIMARY KEY,
    source TEXT,
    source_id INT,
    exam TEXT,
    topic_id INT,
    topic_label TEXT,
    probability FLOAT,
    model_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")

cur.execute("""
CREATE TABLE analytics_papers (
    paper_id INT,
    exam TEXT,
    difficulty_score FLOAT,
    difficulty_label TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute(""" 
CREATE TABLE analytics_fusion (
    id SERIAL PRIMARY KEY,
    exam TEXT,
    year INT,
    tweet_stress_avg FLOAT,
    meme_stress_avg FLOAT,
    paper_difficulty_avg FLOAT,
    fused_difficulty_score FLOAT,
    difficulty_label TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 3. 🔥 NEW: Knowledge Graph Table (MISSING FROM YOUR SCRIPT)
cur.execute("""
CREATE TABLE IF NOT EXISTS knowledge_graph (
    id SERIAL PRIMARY KEY,
    exam VARCHAR(100),
    subject VARCHAR(200),
    topic VARCHAR(200),
    difficulty_score FLOAT,
    difficulty_label VARCHAR(20),
    source VARCHAR(50),
    year VARCHAR(20),
    confidence FLOAT,
    keywords TEXT[],
    text_snippet TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Create indexes for knowledge_graph
cur.execute("CREATE INDEX IF NOT EXISTS idx_kg_exam ON knowledge_graph(exam);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_kg_subject ON knowledge_graph(subject);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_kg_topic ON knowledge_graph(topic);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_kg_difficulty ON knowledge_graph(difficulty_score);")

# 4. Optional: Cache tables for performance
cur.execute("""
CREATE TABLE IF NOT EXISTS decision_tree_cache (
    id SERIAL PRIMARY KEY,
    tree_image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
""")

conn.commit()
cur.close()
conn.close()

print("✅ All tables created successfully including knowledge_graph!")