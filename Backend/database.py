import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get database connection"""
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'exam_ai_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        cursor_factory=RealDictCursor
    )
    return conn

def execute_query(query, params=None):
    """Execute query and return results"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        if query.strip().upper().startswith('SELECT'):
            result = cur.fetchall()
        else:
            conn.commit()
            result = {'affected_rows': cur.rowcount}
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()