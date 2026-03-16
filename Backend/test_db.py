import psycopg2
import pandas as pd

# Connect to database
conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)

print("="*60)
print("📊 NET EXAM DATA CHECK")
print("="*60)

# Check analytics_fusion for NET
df_fusion = pd.read_sql("""
    SELECT * FROM analytics_fusion 
    WHERE exam = 'NET' 
    ORDER BY fused_difficulty_score DESC
""", conn)

print(f"\n📈 analytics_fusion for NET: {len(df_fusion)} rows")
if len(df_fusion) > 0:
    print(df_fusion.to_string())
    
    # Show hard topics (score > 4)
    hard_topics = df_fusion[df_fusion['fused_difficulty_score'] > 4]
    print(f"\n🔥 HARD TOPICS (Score > 4): {len(hard_topics)}")
    if len(hard_topics) > 0:
        for _, row in hard_topics.iterrows():
            print(f"   • Year {row['year']}: Score = {row['fused_difficulty_score']:.2f} ({row['difficulty_label']})")
    
    # Show easy topics (score < 3)
    easy_topics = df_fusion[df_fusion['fused_difficulty_score'] < 3]
    print(f"\n✅ EASY TOPICS (Score < 3): {len(easy_topics)}")
    if len(easy_topics) > 0:
        for _, row in easy_topics.iterrows():
            print(f"   • Year {row['year']}: Score = {row['fused_difficulty_score']:.2f} ({row['difficulty_label']})")
else:
    print("❌ No data found for NET in analytics_fusion")

# Check knowledge_graph for NET
df_kg = pd.read_sql("""
    SELECT * FROM knowledge_graph 
    WHERE exam = 'NET' 
    ORDER BY difficulty_score DESC
""", conn)

print(f"\n📊 knowledge_graph for NET: {len(df_kg)} rows")
if len(df_kg) > 0:
    print(df_kg.to_string())
    
    # Show hard topics
    hard_topics = df_kg[df_kg['difficulty_score'] > 2.5]
    print(f"\n🔥 HARD TOPICS (Score > 2.5): {len(hard_topics)}")
    if len(hard_topics) > 0:
        for _, row in hard_topics.iterrows():
            print(f"   • {row['subject']} - {row['topic']}: Score = {row['difficulty_score']:.2f} ({row['difficulty_label']})")
    
    # Show easy topics
    easy_topics = df_kg[df_kg['difficulty_score'] < 1.8]
    print(f"\n✅ EASY TOPICS (Score < 1.8): {len(easy_topics)}")
    if len(easy_topics) > 0:
        for _, row in easy_topics.iterrows():
            print(f"   • {row['subject']} - {row['topic']}: Score = {row['difficulty_score']:.2f} ({row['difficulty_label']})")
else:
    print("❌ No data found for NET in knowledge_graph")

# Check what exams are available
df_all = pd.read_sql("SELECT DISTINCT exam FROM analytics_fusion", conn)
print(f"\n📌 Available exams in analytics_fusion: {', '.join(df_all['exam'].tolist())}")

df_kg_all = pd.read_sql("SELECT DISTINCT exam FROM knowledge_graph", conn)
print(f"📌 Available exams in knowledge_graph: {', '.join(df_kg_all['exam'].tolist()) if len(df_kg_all) > 0 else 'None'}")

conn.close()