# import psycopg2
# import pandas as pd
# import os
# import json
# import ast
# from psycopg2.extras import Json as PgJson

# # Database connection
# conn = psycopg2.connect(
#     dbname="exam_ai_db",
#     user="postgres",
#     password="password",
#     host="localhost",
#     port="5432"
# )

# conn.autocommit = True
# cur = conn.cursor()

# print("="*80)
# print("📥 IMPORTING KNOWLEDGE GRAPH CSV FILES TO POSTGRESQL")
# print("="*80)

# # Knowledge Graph CSV files to import
# kg_csv_files = {
#     'kg_graph_new_complete.csv': 'kg_graph_new_complete',
#     'kg_graph_new_valid.csv': 'kg_graph_new_valid',
#     'decision_tree_data.csv': 'decision_tree_data',
#     'kg_year_summary.csv': 'kg_year_summary_table',  # Changed name to avoid view conflict
#     'kg_topic_summary.csv': 'kg_topic_summary_table',  # Changed name to avoid view conflict
# }

# def format_postgres_array(keywords_str):
#     """Convert Python list string to PostgreSQL array format"""
#     if pd.isna(keywords_str) or not keywords_str:
#         return None
    
#     try:
#         # If it's already a string representation of a list
#         if isinstance(keywords_str, str):
#             # Try to parse as Python literal
#             try:
#                 keywords_list = ast.literal_eval(keywords_str)
#             except:
#                 # If that fails, try to clean the string
#                 cleaned = keywords_str.replace("'", '"')
#                 try:
#                     keywords_list = json.loads(cleaned)
#                 except:
#                     # Manual parsing as last resort
#                     keywords_list = [k.strip().strip("'\"") for k in keywords_str.strip('[]').split(',')]
            
#             # Convert to PostgreSQL array format
#             if keywords_list and isinstance(keywords_list, list):
#                 # Clean each keyword
#                 cleaned_keywords = []
#                 for k in keywords_list:
#                     if k:
#                         k = str(k).strip().strip("'\"")
#                         if k:
#                             cleaned_keywords.append(k)
                
#                 if cleaned_keywords:
#                     # Return as PostgreSQL array literal
#                     return '{' + ','.join(f'"{k}"' for k in cleaned_keywords) + '}'
#     except Exception as e:
#         print(f"   Warning: Could not parse keywords: {keywords_str[:50]}... Error: {e}")
    
#     return None


# def create_kg_complete_table(table_name):
#     """Create kg_graph_new_complete table"""
#     print(f"\n🏗️  Creating table: {table_name}")
    
#     # Drop table if exists (CASCADE will handle dependencies)
#     cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
    
#     # Create table with appropriate schema
#     create_stmt = f"""
#     CREATE TABLE {table_name} (
#         id SERIAL PRIMARY KEY,
#         exam VARCHAR(100),
#         year VARCHAR(20),
#         source VARCHAR(50),
#         source_id INTEGER,
#         subject VARCHAR(200),
#         topic VARCHAR(200),
#         difficulty_score FLOAT,
#         difficulty_label VARCHAR(20),
#         confidence FLOAT,
#         keywords TEXT[],
#         text_snippet TEXT,
#         tweet_stress_avg FLOAT,
#         tweet_sentiment_score FLOAT,
#         tweet_sentiment_label VARCHAR(20),
#         tweet_count INTEGER DEFAULT 1,
#         meme_stress_avg FLOAT,
#         meme_sarcasm_score FLOAT,
#         meme_is_sarcastic BOOLEAN,
#         meme_count INTEGER DEFAULT 1,
#         paper_difficulty_avg FLOAT,
#         paper_count INTEGER DEFAULT 1,
#         total_occurrences INTEGER DEFAULT 1,
#         avg_fused_difficulty FLOAT,
#         is_valid BOOLEAN DEFAULT TRUE,
#         validation_reason TEXT,
#         subject_confidence FLOAT,
#         topic_confidence FLOAT,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     );
#     """
    
#     cur.execute(create_stmt)
#     print(f"✅ Created table: {table_name}")
    
#     # Create indexes
#     print(f"   Creating indexes...")
#     cur.execute(f"CREATE INDEX idx_{table_name}_exam ON {table_name}(exam);")
#     cur.execute(f"CREATE INDEX idx_{table_name}_subject ON {table_name}(subject);")
#     cur.execute(f"CREATE INDEX idx_{table_name}_topic ON {table_name}(topic);")
#     cur.execute(f"CREATE INDEX idx_{table_name}_difficulty ON {table_name}(difficulty_label);")
#     cur.execute(f"CREATE INDEX idx_{table_name}_valid ON {table_name}(is_valid);")
#     print(f"✅ Created indexes for {table_name}")


# def create_decision_tree_table(table_name):
#     """Create decision_tree_data table"""
#     print(f"\n🏗️  Creating table: {table_name}")
    
#     cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
    
#     create_stmt = f"""
#     CREATE TABLE {table_name} (
#         id SERIAL PRIMARY KEY,
#         exam VARCHAR(100),
#         subject VARCHAR(200),
#         topic VARCHAR(200),
#         feature_vector JSONB,
#         target_label VARCHAR(20),
#         confidence FLOAT,
#         source_count INTEGER,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     );
#     """
    
#     cur.execute(create_stmt)
#     print(f"✅ Created table: {table_name}")
    
#     # Create indexes
#     cur.execute(f"CREATE INDEX idx_{table_name}_exam ON {table_name}(exam);")
#     cur.execute(f"CREATE INDEX idx_{table_name}_subject ON {table_name}(subject);")
#     print(f"✅ Created indexes for {table_name}")


# def create_summary_table(table_name, table_type):
#     """Create summary tables"""
#     print(f"\n🏗️  Creating table: {table_name}")
    
#     # Drop the view first if it exists (since these names might conflict with views)
#     try:
#         cur.execute(f"DROP VIEW IF EXISTS {table_name} CASCADE;")
#     except:
#         pass
    
#     # Drop table if exists
#     cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
    
#     if table_type == 'year':
#         create_stmt = f"""
#         CREATE TABLE {table_name} (
#             id SERIAL PRIMARY KEY,
#             exam VARCHAR(100),
#             year VARCHAR(20),
#             subjects_covered INTEGER,
#             topics_covered INTEGER,
#             total_entries INTEGER,
#             avg_difficulty FLOAT,
#             avg_tweet_stress FLOAT,
#             avg_meme_stress FLOAT,
#             avg_paper_difficulty FLOAT,
#             avg_fused_difficulty FLOAT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );
#         """
#     else:  # topic summary
#         create_stmt = f"""
#         CREATE TABLE {table_name} (
#             id SERIAL PRIMARY KEY,
#             exam VARCHAR(100),
#             subject VARCHAR(200),
#             topic VARCHAR(200),
#             occurrences INTEGER,
#             avg_difficulty FLOAT,
#             avg_tweet_stress FLOAT,
#             avg_meme_stress FLOAT,
#             avg_paper_difficulty FLOAT,
#             avg_fused_difficulty FLOAT,
#             total_tweets INTEGER,
#             total_memes INTEGER,
#             total_papers INTEGER,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );
#         """
    
#     cur.execute(create_stmt)
#     print(f"✅ Created table: {table_name}")
    
#     # Create indexes
#     if table_type == 'year':
#         cur.execute(f"CREATE INDEX idx_{table_name}_exam ON {table_name}(exam);")
#         cur.execute(f"CREATE INDEX idx_{table_name}_year ON {table_name}(year);")
#     else:
#         cur.execute(f"CREATE INDEX idx_{table_name}_exam ON {table_name}(exam);")
#         cur.execute(f"CREATE INDEX idx_{table_name}_subject ON {table_name}(subject);")
#         cur.execute(f"CREATE INDEX idx_{table_name}_topic ON {table_name}(topic);")
    
#     print(f"✅ Created indexes for {table_name}")


# def import_kg_complete(csv_file, table_name):
#     """Import kg_graph_new_complete.csv"""
#     print(f"\n📄 Processing: {csv_file}")
    
#     if not os.path.exists(csv_file):
#         print(f"⚠️  File not found: {csv_file}")
#         return False
    
#     try:
#         # Read CSV
#         df = pd.read_csv(csv_file)
#         print(f"   Found {len(df)} rows, {len(df.columns)} columns")
        
#         # Create table
#         create_kg_complete_table(table_name)
        
#         # Insert data in batches
#         batch_size = 100
#         total_rows = len(df)
        
#         print(f"   Inserting {total_rows} rows in batches of {batch_size}...")
        
#         insert_stmt = f"""
#             INSERT INTO {table_name} (
#                 exam, year, source, source_id, subject, topic, 
#                 difficulty_score, difficulty_label, confidence, keywords, text_snippet,
#                 tweet_stress_avg, tweet_sentiment_score, tweet_sentiment_label, tweet_count,
#                 meme_stress_avg, meme_sarcasm_score, meme_is_sarcastic, meme_count,
#                 paper_difficulty_avg, paper_count, total_occurrences, avg_fused_difficulty,
#                 is_valid, validation_reason, subject_confidence, topic_confidence
#             ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
        
#         for i in range(0, total_rows, batch_size):
#             batch = df.iloc[i:i+batch_size]
#             records = []
            
#             for _, row in batch.iterrows():
#                 # Format keywords as PostgreSQL array
#                 keywords = format_postgres_array(row.get('keywords'))
                
#                 record = (
#                     row.get('exam'), 
#                     str(row.get('year')) if not pd.isna(row.get('year')) else None,
#                     row.get('source'),
#                     int(row.get('source_id')) if not pd.isna(row.get('source_id')) else None,
#                     row.get('subject'),
#                     row.get('topic'),
#                     float(row.get('difficulty_score')) if not pd.isna(row.get('difficulty_score')) else None,
#                     row.get('difficulty_label'),
#                     float(row.get('confidence')) if not pd.isna(row.get('confidence')) else None,
#                     keywords,  # Now properly formatted for PostgreSQL
#                     row.get('text_snippet'),
#                     float(row.get('tweet_stress_avg')) if not pd.isna(row.get('tweet_stress_avg')) else None,
#                     float(row.get('tweet_sentiment_score')) if not pd.isna(row.get('tweet_sentiment_score')) else None,
#                     row.get('tweet_sentiment_label'),
#                     int(row.get('tweet_count')) if not pd.isna(row.get('tweet_count')) else 1,
#                     float(row.get('meme_stress_avg')) if not pd.isna(row.get('meme_stress_avg')) else None,
#                     float(row.get('meme_sarcasm_score')) if not pd.isna(row.get('meme_sarcasm_score')) else None,
#                     bool(row.get('meme_is_sarcastic')) if not pd.isna(row.get('meme_is_sarcastic')) else False,
#                     int(row.get('meme_count')) if not pd.isna(row.get('meme_count')) else 1,
#                     float(row.get('paper_difficulty_avg')) if not pd.isna(row.get('paper_difficulty_avg')) else None,
#                     int(row.get('paper_count')) if not pd.isna(row.get('paper_count')) else 1,
#                     int(row.get('total_occurrences')) if not pd.isna(row.get('total_occurrences')) else 1,
#                     float(row.get('avg_fused_difficulty')) if not pd.isna(row.get('avg_fused_difficulty')) else None,
#                     bool(row.get('is_valid')) if not pd.isna(row.get('is_valid')) else True,
#                     row.get('validation_reason'),
#                     float(row.get('subject_confidence')) if not pd.isna(row.get('subject_confidence')) else None,
#                     float(row.get('topic_confidence')) if not pd.isna(row.get('topic_confidence')) else None
#                 )
#                 records.append(record)
            
#             # Execute batch insert
#             cur.executemany(insert_stmt, records)
#             print(f"   Progress: {min(i+batch_size, total_rows)}/{total_rows} rows")
        
#         print(f"✅ Successfully imported {total_rows} rows into {table_name}")
#         return True
        
#     except Exception as e:
#         print(f"❌ Error importing {csv_file}: {e}")
#         import traceback
#         traceback.print_exc()
#         return False


# def import_decision_tree(csv_file, table_name):
#     """Import decision_tree_data.csv"""
#     print(f"\n📄 Processing: {csv_file}")
    
#     if not os.path.exists(csv_file):
#         print(f"⚠️  File not found: {csv_file}")
#         return False
    
#     try:
#         df = pd.read_csv(csv_file)
#         print(f"   Found {len(df)} rows, {len(df.columns)} columns")
        
#         create_decision_tree_table(table_name)
        
#         batch_size = 100
#         total_rows = len(df)
        
#         print(f"   Inserting {total_rows} rows...")
        
#         insert_stmt = f"""
#             INSERT INTO {table_name} (exam, subject, topic, feature_vector, target_label, confidence, source_count)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#         """
        
#         for i in range(0, total_rows, batch_size):
#             batch = df.iloc[i:i+batch_size]
#             records = []
            
#             for _, row in batch.iterrows():
#                 # Handle JSONB column
#                 feature_vector = row.get('feature_vector')
#                 if feature_vector and not pd.isna(feature_vector):
#                     if isinstance(feature_vector, str):
#                         # Fix single quotes to double quotes for JSON
#                         feature_vector = feature_vector.replace("'", '"')
#                         try:
#                             feature_vector = json.loads(feature_vector)
#                         except:
#                             # If still fails, try to parse as Python dict
#                             try:
#                                 feature_vector = ast.literal_eval(row.get('feature_vector'))
#                             except:
#                                 feature_vector = {}
                
#                 record = (
#                     row.get('exam'),
#                     row.get('subject'),
#                     row.get('topic'),
#                     PgJson(feature_vector) if feature_vector else None,
#                     row.get('target_label'),
#                     float(row.get('confidence')) if not pd.isna(row.get('confidence')) else None,
#                     int(row.get('source_count')) if not pd.isna(row.get('source_count')) else None
#                 )
#                 records.append(record)
            
#             cur.executemany(insert_stmt, records)
#             print(f"   Progress: {min(i+batch_size, total_rows)}/{total_rows} rows")
        
#         print(f"✅ Successfully imported {total_rows} rows into {table_name}")
#         return True
        
#     except Exception as e:
#         print(f"❌ Error importing {csv_file}: {e}")
#         import traceback
#         traceback.print_exc()
#         return False


# def import_summary(csv_file, table_name, table_type):
#     """Import summary CSV files"""
#     print(f"\n📄 Processing: {csv_file}")
    
#     if not os.path.exists(csv_file):
#         print(f"⚠️  File not found: {csv_file}")
#         return False
    
#     try:
#         df = pd.read_csv(csv_file)
#         print(f"   Found {len(df)} rows, {len(df.columns)} columns")
        
#         create_summary_table(table_name, table_type)
        
#         batch_size = 100
#         total_rows = len(df)
        
#         print(f"   Inserting {total_rows} rows...")
        
#         if table_type == 'year':
#             insert_stmt = f"""
#                 INSERT INTO {table_name} (
#                     exam, year, subjects_covered, topics_covered, total_entries,
#                     avg_difficulty, avg_tweet_stress, avg_meme_stress, avg_paper_difficulty, avg_fused_difficulty
#                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
#         else:  # topic summary
#             insert_stmt = f"""
#                 INSERT INTO {table_name} (
#                     exam, subject, topic, occurrences, avg_difficulty,
#                     avg_tweet_stress, avg_meme_stress, avg_paper_difficulty, avg_fused_difficulty,
#                     total_tweets, total_memes, total_papers
#                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
        
#         for i in range(0, total_rows, batch_size):
#             batch = df.iloc[i:i+batch_size]
#             records = []
            
#             for _, row in batch.iterrows():
#                 if table_type == 'year':
#                     record = (
#                         row.get('exam'),
#                         str(row.get('year')) if not pd.isna(row.get('year')) else None,
#                         int(row.get('subjects_covered')) if not pd.isna(row.get('subjects_covered')) else 0,
#                         int(row.get('topics_covered')) if not pd.isna(row.get('topics_covered')) else 0,
#                         int(row.get('total_entries')) if not pd.isna(row.get('total_entries')) else 0,
#                         float(row.get('avg_difficulty')) if not pd.isna(row.get('avg_difficulty')) else None,
#                         float(row.get('avg_tweet_stress')) if not pd.isna(row.get('avg_tweet_stress')) else None,
#                         float(row.get('avg_meme_stress')) if not pd.isna(row.get('avg_meme_stress')) else None,
#                         float(row.get('avg_paper_difficulty')) if not pd.isna(row.get('avg_paper_difficulty')) else None,
#                         float(row.get('avg_fused_difficulty')) if not pd.isna(row.get('avg_fused_difficulty')) else None
#                     )
#                 else:
#                     record = (
#                         row.get('exam'),
#                         row.get('subject'),
#                         row.get('topic'),
#                         int(row.get('occurrences')) if not pd.isna(row.get('occurrences')) else 0,
#                         float(row.get('avg_difficulty')) if not pd.isna(row.get('avg_difficulty')) else None,
#                         float(row.get('avg_tweet_stress')) if not pd.isna(row.get('avg_tweet_stress')) else None,
#                         float(row.get('avg_meme_stress')) if not pd.isna(row.get('avg_meme_stress')) else None,
#                         float(row.get('avg_paper_difficulty')) if not pd.isna(row.get('avg_paper_difficulty')) else None,
#                         float(row.get('avg_fused_difficulty')) if not pd.isna(row.get('avg_fused_difficulty')) else None,
#                         int(row.get('total_tweets')) if not pd.isna(row.get('total_tweets')) else 0,
#                         int(row.get('total_memes')) if not pd.isna(row.get('total_memes')) else 0,
#                         int(row.get('total_papers')) if not pd.isna(row.get('total_papers')) else 0
#                     )
#                 records.append(record)
            
#             cur.executemany(insert_stmt, records)
#             print(f"   Progress: {min(i+batch_size, total_rows)}/{total_rows} rows")
        
#         print(f"✅ Successfully imported {total_rows} rows into {table_name}")
#         return True
        
#     except Exception as e:
#         print(f"❌ Error importing {csv_file}: {e}")
#         import traceback
#         traceback.print_exc()
#         return False


# def import_all_kg_files():
#     """Import all knowledge graph CSV files"""
#     success_count = 0
#     fail_count = 0
    
#     # Import kg_graph_new_complete.csv
#     if import_kg_complete('kg_graph_new_complete.csv', 'kg_graph_new_complete'):
#         success_count += 1
#     else:
#         fail_count += 1
    
#     # Import kg_graph_new_valid.csv (if exists)
#     if os.path.exists('kg_graph_new_valid.csv'):
#         if import_kg_complete('kg_graph_new_valid.csv', 'kg_graph_new_valid'):
#             success_count += 1
#         else:
#             fail_count += 1
#     else:
#         print(f"\n⚠️  Skipping kg_graph_new_valid.csv (not found)")
    
#     # Import decision_tree_data.csv
#     if import_decision_tree('decision_tree_data.csv', 'decision_tree_data'):
#         success_count += 1
#     else:
#         fail_count += 1
    
#     # Import kg_year_summary.csv
#     if import_summary('kg_year_summary.csv', 'kg_year_summary_data', 'year'):
#         success_count += 1
#     else:
#         fail_count += 1
    
#     # Import kg_topic_summary.csv
#     if import_summary('kg_topic_summary.csv', 'kg_topic_summary_data', 'topic'):
#         success_count += 1
#     else:
#         fail_count += 1
    
#     return success_count, fail_count


# def verify_imports():
#     """Verify that imports were successful"""
#     print("\n🔍 Verifying imports...")
    
#     tables = [
#         'kg_graph_new_complete',
#         'decision_tree_data',
#         'kg_year_summary_data',
#         'kg_topic_summary_data'
#     ]
    
#     # Check if kg_graph_new_valid exists
#     cur.execute("""
#         SELECT EXISTS (
#             SELECT FROM information_schema.tables 
#             WHERE table_name = 'kg_graph_new_valid'
#         );
#     """)
#     if cur.fetchone()[0]:
#         tables.insert(1, 'kg_graph_new_valid')
    
#     print("\n📋 Imported tables:")
#     print("-" * 60)
#     for table in tables:
#         try:
#             cur.execute(f"SELECT COUNT(*) FROM {table}")
#             count = cur.fetchone()[0]
#             print(f"   • {table:<30}: {count:>10} rows")
#         except Exception as e:
#             print(f"   • {table:<30}: Error - {e}")
    
#     # Show sample from each table
#     print("\n📊 Sample data from each table:")
#     print("-" * 80)
    
#     for table in tables[:3]:  # Show first 3 tables
#         try:
#             cur.execute(f"SELECT * FROM {table} LIMIT 1")
#             sample = cur.fetchone()
#             if sample:
#                 print(f"\n{table}:")
#                 for key, value in sample.items():
#                     if key not in ['keywords', 'feature_vector', 'text_snippet']:
#                         if value and len(str(value)) > 50:
#                             value = str(value)[:50] + "..."
#                         print(f"   {key}: {value}")
#         except Exception as e:
#             print(f"\n{table}: Error - {e}")


# def main():
#     try:
#         print("\n🚀 Starting Knowledge Graph CSV Import...")
        
#         # Import all KG files
#         success, fail = import_all_kg_files()
        
#         # Verify imports
#         verify_imports()
        
#         print("\n" + "✅"*50)
#         print("✅ KNOWLEDGE GRAPH CSV IMPORT COMPLETED!")
#         print(f"✅ Successfully imported: {success} files")
#         print(f"❌ Failed imports: {fail} files")
#         print("✅"*50)
        
#     except Exception as e:
#         print(f"\n❌ Error: {e}")
#         import traceback
#         traceback.print_exc()
#     finally:
#         conn.close()

# if __name__ == "__main__":
#     main()

import os
import pandas as pd
import psycopg2
import json
import ast
from psycopg2.extras import execute_batch

conn = psycopg2.connect(
    host="localhost",
    database="exam_ai_db",
    user="postgres",
    password="password"
)

cursor = conn.cursor()

folder = r"F:\Smart_Score AI\Backend\Structured_Data"

print("\n🚀 Starting CSV Import\n")

for file in os.listdir(folder):

    if file.endswith(".csv"):

        path = os.path.join(folder, file)
        table = file.replace(".csv","").lower()

        print(f"\n📂 Processing: {file}")

        df = pd.read_csv(path, engine="python")

        # remove unwanted columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # clean column names
        df.columns = [c.strip().replace(" ","_").lower() for c in df.columns]

        df = df.fillna("")

        # convert keywords to json
        if "keywords" in df.columns:

            def fix_keywords(x):
                try:
                    return json.dumps(ast.literal_eval(x))
                except:
                    return json.dumps([])

            df["keywords"] = df["keywords"].apply(fix_keywords)

        # CREATE TABLE
        cols_def = []
        for c in df.columns:
            if c == "keywords":
                cols_def.append(f'"{c}" JSONB')
            else:
                cols_def.append(f'"{c}" TEXT')

        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table} (
        {",".join(cols_def)}
        )
        """

        cursor.execute(create_sql)
        conn.commit()

        # PREPARE INSERT
        cols = ",".join([f'"{c}"' for c in df.columns])

        placeholders = []
        for c in df.columns:
            if c == "keywords":
                placeholders.append("%s::jsonb")
            else:
                placeholders.append("%s")

        insert_sql = f"""
        INSERT INTO {table} ({cols})
        VALUES ({",".join(placeholders)})
        """

        data = [tuple(row) for row in df.values]

        execute_batch(cursor, insert_sql, data, page_size=1000)

        conn.commit()

        print(f"✅ Imported {table}")

cursor.close()
conn.close()

print("\n🎉 ALL CSV FILES IMPORTED SUCCESSFULLY")