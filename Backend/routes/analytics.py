from flask import Blueprint, jsonify
from db import get_db

analytics_api = Blueprint("analytics_api", __name__)

@analytics_api.route("/topics", methods=["GET"])
def difficult_topics():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT subject, topic, COUNT(*)
        FROM papers_raw
        WHERE difficulty='Hard'
        GROUP BY subject, topic
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {"subject": r[0], "topic": r[1], "count": r[2]}
        for r in rows
    ])