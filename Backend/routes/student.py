from flask import Blueprint, request, jsonify
from db import get_db

student_api = Blueprint("student_api", __name__)

@student_api.route("/stress", methods=["GET"])
def tweet_stress():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT exam, AVG(stress_score)
        FROM analytics_tweets
        GROUP BY exam
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {"exam": r[0], "avg_stress": float(r[1])}
        for r in data
    ])