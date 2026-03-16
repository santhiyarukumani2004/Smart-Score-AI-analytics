from flask import Blueprint, jsonify
from db import get_db

teacher_api = Blueprint("teacher_api", __name__)

@teacher_api.route("/difficulty", methods=["GET"])
def difficulty_graph():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT exam, difficulty_label, COUNT(*)
        FROM analytics_papers
        GROUP BY exam, difficulty_label
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {"exam": r[0], "level": r[1], "count": r[2]}
        for r in rows
    ])