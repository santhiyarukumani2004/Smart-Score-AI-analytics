from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import logging
from datetime import datetime, timedelta
import os
import traceback

app = Flask(__name__)
app.secret_key = "exam_ai_secret"
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Enable CORS for all routes
CORS(app, supports_credentials=True, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3008"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="exam_ai_db",
            user="postgres",
            password="password",
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=None):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("No database connection")
            return []
        
        cur = conn.cursor()
        
        if params is not None:
            if not isinstance(params, (tuple, list)):
                params = (params,)
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            result = cur.fetchall()
            return result
        else:
            conn.commit()
            return {'affected_rows': cur.rowcount}
            
    except Exception as e:
        logger.error(f"Query error: {e}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# LOGIN PAGE
# -----------------------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username == "student" and password == "123":
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
            
    return render_template("login.html")


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


# -----------------------------
# STUDENT DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# -----------------------------
# API: STUDENT REGISTRATION
# -----------------------------
@app.route('/api/student/register', methods=['POST', 'OPTIONS'])
def student_register():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        data = request.json
        logger.info(f"Student registration data: {data}")
        
        session['user_type'] = 'student'
        session['user_data'] = data
        
        exam_name = data.get('competitiveExam') or data.get('course') or 'General'
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'data': data,
            'exam': exam_name
        })
        
    except Exception as e:
        logger.error(f"Student registration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/student/dashboard/<exam>', methods=['GET'])
def student_dashboard(exam):
    try:
        exam_upper = exam.upper()
        
        # Exam name mapping - handle both NET and UGC NET
        exam_mapping = {
            'NET': 'UGC NET',
            'UGC NET': 'UGC NET',
            'NTA NET': 'UGC NET',
            'CSIR NET': 'UGC NET',
            'JEE': 'JEE',
            'JEE MAIN': 'JEE',
            'NEET': 'NEET',
            'GATE': 'GATE',
            'TNPSC': 'TNPSC',
            'UPSC': 'UPSC'
        }
        
        # Get the correct database exam name
        db_exam = exam_mapping.get(exam_upper, exam_upper)
        logger.info(f"Mapped {exam_upper} to {db_exam}")
        logger.info(f"Fetching dashboard data for exam: {db_exam}")

        # Initialize all variables at the beginning
        tweet_stats = {}
        tweet_trend_data = []
        meme_stats = {}
        meme_trend_data = []
        meme_count_by_year = []
        yearly_stress_distribution = []
        difficulty_classification = []
        year_difficulty_data = []
        stress_distribution_pie = {}
        subject_comparison = []
        topic_rankings = []
        topics_for_component = []
        top3_hardest = []
        top3_easiest = []
        most_difficult_topics = []
        difficulty_distribution = {'hard': 0, 'medium': 0, 'easy': 0, 'total': 0, 'hard_pct': 0, 'medium_pct': 0, 'easy_pct': 0}
        topics_over_100 = []
        ai_recommendations = []

        # =====================================
        # 1️⃣ TWEET STRESS DATA FROM analytics_tweets_exam
        # =====================================
        tweet_query = """
        SELECT 
            tweet_count,
            overall_stress,
            high_stress, medium_stress, low_stress,
            high_stress_pct, medium_stress_pct, low_stress_pct,
            positive_sentiment, negative_sentiment, neutral_sentiment,
            positive_pct, negative_pct, neutral_pct,
            avg_difficulty,
            topic_count
        FROM analytics_tweets_exam
        WHERE UPPER(exam) = UPPER(%s)
        """
        tweet_result = execute_query(tweet_query, (db_exam,))
        
        if tweet_result and len(tweet_result) > 0:
            tweet_stats = dict(tweet_result[0])
            logger.info(f"Tweet stats from analytics_tweets_exam: {tweet_stats}")
        else:
            tweet_stats = get_tweet_stats_from_knowledgegraph(db_exam)
        
        # =====================================
        # 2️⃣ TWEET YEARLY TREND FROM year_summary
        # =====================================
        tweet_yearly_query = """
        SELECT 
            year,
            avg_tweet_stress as stress,
            total_entries as count
        FROM year_summary
        WHERE UPPER(exam) = UPPER(%s) AND year BETWEEN 2023 AND 2026
        ORDER BY year
        """
        tweet_yearly = execute_query(tweet_yearly_query, (db_exam,))
        
        if tweet_yearly:
            for row in tweet_yearly:
                tweet_trend_data.append({
                    'year': str(row['year']),
                    'stress': round(float(row['stress']), 1),
                    'count': row['count']
                })
        logger.info(f"Tweet yearly data: {tweet_trend_data}")
        
        # =====================================
        # 3️⃣ MEME DATA FROM analytics_memes
        # =====================================
        meme_query = """
            SELECT 
                total_memes as meme_count,
                overall_stress_pct as avg_stress,
                high_stress_count as high_stress,
                medium_stress_count as medium_stress,
                low_stress_count as low_stress,
                high_stress_pct,
                medium_stress_pct,
                low_stress_pct,
                avg_sarcasm_score as avg_sarcasm,
                sarcastic_count,
                non_sarcastic_count as nonsarcastic_count,
                sarcastic_pct,
                non_sarcastic_pct as nonsarcastic_pct,
                positive_sentiment_pct,
                negative_sentiment_pct,
                neutral_sentiment_pct,
                difficulty_signal_count,
                difficulty_signal_pct,
                avg_emoji_score
            FROM analytics_memes
            WHERE UPPER(exam) = UPPER(%s)
        """
        meme_result = execute_query(meme_query, (db_exam,))
        logger.info(f"Meme stats from analytics_memes: {meme_result}")

        if meme_result and len(meme_result) > 0:
            if isinstance(meme_result[0], dict):
                meme_stats = dict(meme_result[0])
            else:
                meme_stats = {
                    "meme_count": meme_result[0][0] if len(meme_result[0]) > 0 else 0,
                    "avg_stress": meme_result[0][1] if len(meme_result[0]) > 1 else 0,
                    "high_stress": meme_result[0][2] if len(meme_result[0]) > 2 else 0,
                    "medium_stress": meme_result[0][3] if len(meme_result[0]) > 3 else 0,
                    "low_stress": meme_result[0][4] if len(meme_result[0]) > 4 else 0,
                    "high_stress_pct": meme_result[0][5] if len(meme_result[0]) > 5 else 0,
                    "medium_stress_pct": meme_result[0][6] if len(meme_result[0]) > 6 else 0,
                    "low_stress_pct": meme_result[0][7] if len(meme_result[0]) > 7 else 0,
                    "avg_sarcasm": meme_result[0][8] if len(meme_result[0]) > 8 else 0,
                    "sarcastic_count": meme_result[0][9] if len(meme_result[0]) > 9 else 0,
                    "nonsarcastic_count": meme_result[0][10] if len(meme_result[0]) > 10 else 0,
                    "sarcastic_pct": meme_result[0][11] if len(meme_result[0]) > 11 else 0,
                    "nonsarcastic_pct": meme_result[0][12] if len(meme_result[0]) > 12 else 0
                }
            logger.info(f"✅ Processed meme stats: {meme_stats}")
        else:
            meme_stats = {
                "meme_count": 0, "avg_stress": 0, "high_stress": 0, "medium_stress": 0, "low_stress": 0,
                "high_stress_pct": 0, "medium_stress_pct": 0, "low_stress_pct": 0, "avg_sarcasm": 0,
                "sarcastic_count": 0, "nonsarcastic_count": 0, "sarcastic_pct": 0, "nonsarcastic_pct": 0
            }
            logger.warning(f"No meme data found for {db_exam}")

        # =====================================
        # 4️⃣ MEME YEARLY TREND FROM year_summary
        # =====================================
        meme_yearly_query = """
            SELECT 
                year,
                avg_meme_stress as stress,
                total_entries as count
            FROM year_summary
            WHERE UPPER(exam) = UPPER(%s) AND year BETWEEN 2023 AND 2026
            ORDER BY year
        """
        meme_yearly = execute_query(meme_yearly_query, (db_exam,))
        logger.info(f"Meme yearly raw data for {db_exam}: {meme_yearly}")

        if meme_yearly and len(meme_yearly) > 0:
            for row in meme_yearly:
                try:
                    if isinstance(row, dict):
                        year_val = row.get('year')
                        stress_val = row.get('stress')
                        count_val = row.get('count')
                    else:
                        year_val = row[0] if len(row) > 0 else None
                        stress_val = row[1] if len(row) > 1 else None
                        count_val = row[2] if len(row) > 2 else None
                    
                    if year_val is not None:
                        meme_trend_data.append({
                            'year': str(year_val),
                            'stress': round(float(stress_val), 1) if stress_val is not None else 0,
                            'count': int(count_val) if count_val is not None else 0
                        })
                        meme_count_by_year.append({
                            'year': str(year_val),
                            'count': int(count_val) if count_val is not None else 0
                        })
                except Exception as e:
                    logger.error(f"Error processing meme yearly row {row}: {e}")
                    continue 
            
            logger.info(f"✅ Processed {len(meme_trend_data)} years of meme data: {meme_trend_data}")
            logger.info(f"✅ Meme count by year: {meme_count_by_year}")

        # =====================================
        # 5️⃣ YEARLY STRESS DISTRIBUTION
        # =====================================
        if meme_trend_data and meme_stats.get('meme_count', 0) > 0:
            for year_item in meme_trend_data:
                year = year_item['year']
                year_total = year_item['count']
                
                if year_total > 0:
                    total_actual = meme_stats['meme_count']
                    
                    high_prop = meme_stats.get('high_stress', 0) / total_actual if total_actual > 0 else 0
                    medium_prop = meme_stats.get('medium_stress', 0) / total_actual if total_actual > 0 else 0
                    low_prop = meme_stats.get('low_stress', 0) / total_actual if total_actual > 0 else 0
                    
                    high_count = round(year_total * high_prop)
                    medium_count = round(year_total * medium_prop)
                    low_count = year_total - high_count - medium_count
                    
                    high_count = max(0, high_count)
                    medium_count = max(0, medium_count)
                    low_count = max(0, low_count)
                    
                    yearly_stress_distribution.append({
                        'year': year,
                        'high_stress': high_count,
                        'medium_stress': medium_count,
                        'low_stress': low_count,
                        'total': year_total
                    })
                else:
                    yearly_stress_distribution.append({
                        'year': year,
                        'high_stress': 0,
                        'medium_stress': 0,
                        'low_stress': 0,
                        'total': 0
                    })
            
            logger.info(f"✅ Created yearly stress distribution: {yearly_stress_distribution}")

        # =====================================
        # 6️⃣ DIFFICULTY CLASSIFICATION FROM exam_summary
        # =====================================
        difficulty_query = """
            SELECT 
                difficulty_label,
                COUNT(*) as count
            FROM exam_summary
            WHERE UPPER(exam) = UPPER(%s) AND difficulty_label IS NOT NULL
            GROUP BY difficulty_label
            ORDER BY 
                CASE LOWER(difficulty_label)
                    WHEN 'hard' THEN 1
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'easy' THEN 3
                    WHEN 'low' THEN 3
                    ELSE 4
                END
        """
        difficulty_result = execute_query(difficulty_query, (db_exam,))
        logger.info(f"Difficulty classification raw data: {difficulty_result}")
        
        total = 0

        if difficulty_result and len(difficulty_result) > 0:
            for row in difficulty_result:
                total += row['count']
            
            for row in difficulty_result:
                label = row['difficulty_label'].lower()
                if label in ['hard', 'high']:
                    display_label = 'Hard'
                elif label in ['medium']:
                    display_label = 'Medium'
                elif label in ['easy', 'low']:
                    display_label = 'Easy'
                else:
                    display_label = label.capitalize()
                
                difficulty_classification.append({
                    'level': display_label,
                    'count': row['count'],
                    'percentage': round(row['count'] / total * 100, 1) if total > 0 else 0
                })
            
            logger.info(f"✅ Processed difficulty classification: {difficulty_classification}")

        # =====================================
        # 7️⃣ YEAR-WISE DIFFICULTY TRENDS
        # =====================================
        year_difficulty_query = """
            SELECT 
                year,
                avg_tweet_stress as tweet_stress,
                avg_meme_stress as meme_stress,
                avg_paper_difficulty as paper_difficulty,
                avg_fused_difficulty as fused_difficulty,
                total_entries
            FROM year_summary
            WHERE UPPER(exam) = UPPER(%s) 
                AND year BETWEEN 2023 AND 2026
            ORDER BY year
        """
        year_difficulty_result = execute_query(year_difficulty_query, (db_exam,))
        logger.info(f"Year difficulty raw data: {year_difficulty_result}")

        if year_difficulty_result and len(year_difficulty_result) > 0:
            for row in year_difficulty_result:
                year_difficulty_data.append({
                    'year': str(row['year']),
                    'tweet_stress': round(float(row['tweet_stress'] or 0), 1),
                    'meme_stress': round(float(row['meme_stress'] or 0), 1),
                    'paper_difficulty': round(float(row['paper_difficulty'] or 0), 1),
                    'fused_difficulty': round(float(row['fused_difficulty'] or 0), 1),
                    'total_entries': row['total_entries'] or 0
                }) 
            logger.info(f"Processed year difficulty data: {year_difficulty_data}")

        # =====================================
        # 8️⃣ STRESS DISTRIBUTION PIE CHART
        # =====================================
        if year_difficulty_data and len(year_difficulty_data) > 0:
            avg_tweet = sum([item['tweet_stress'] for item in year_difficulty_data]) / len(year_difficulty_data)
            avg_meme = sum([item['meme_stress'] for item in year_difficulty_data]) / len(year_difficulty_data)
            avg_paper = sum([item['paper_difficulty'] for item in year_difficulty_data]) / len(year_difficulty_data)
            
            stress_distribution_pie = {
                'tweet_stress': round(avg_tweet, 1),
                'meme_stress': round(avg_meme, 1),
                'paper_difficulty': round(avg_paper, 1),
                'total': round(avg_tweet + avg_meme + avg_paper, 1)
            }
            
            total_stress = stress_distribution_pie['total']
            if total_stress > 0:
                stress_distribution_pie['tweet_pct'] = round((avg_tweet / total_stress) * 100, 1)
                stress_distribution_pie['meme_pct'] = round((avg_meme / total_stress) * 100, 1)
                stress_distribution_pie['paper_pct'] = round((avg_paper / total_stress) * 100, 1)
            
            logger.info(f"Stress distribution pie data: {stress_distribution_pie}")

        # =====================================
        # 9️⃣ SUBJECT COMPARISON FROM exam_summary
        # =====================================
        try:
            subject_query = """
                SELECT 
                    subject,
                    COUNT(*) as total_occurrences,
                    COUNT(DISTINCT topic) as unique_topics,
                    AVG(CAST(difficulty_score AS FLOAT)) as avg_difficulty,
                    MIN(CAST(difficulty_score AS FLOAT)) as min_difficulty,
                    MAX(CAST(difficulty_score AS FLOAT)) as max_difficulty
                FROM exam_summary
                WHERE UPPER(exam) = UPPER(%s)
                    AND subject IS NOT NULL
                    AND subject != ''
                GROUP BY subject
                ORDER BY total_occurrences DESC
            """
            
            subject_result = execute_query(subject_query, (db_exam,))
            logger.info(f"📊 Subject result: {subject_result}")
            
            if subject_result and len(subject_result) > 0:
                for row in subject_result:
                    avg_diff = float(row['avg_difficulty']) if row['avg_difficulty'] else 0
                    subject_comparison.append({
                        'subject': row['subject'],
                        'total_occurrences': row['total_occurrences'],
                        'unique_topics': row['unique_topics'],
                        'avg_difficulty': round(avg_diff, 2),
                        'difficulty': round(avg_diff / 5.0, 2),
                        'min_difficulty': round(float(row['min_difficulty']), 2) if row['min_difficulty'] else 0,
                        'max_difficulty': round(float(row['max_difficulty']), 2) if row['max_difficulty'] else 0
                    })
                logger.info(f"✅ Subjects: {[(s['subject'], s['total_occurrences']) for s in subject_comparison]}")
            else:
                logger.warning(f"No subjects found")
        except Exception as e:
            logger.error(f"Subject error: {e}")

        # =====================================
        # 🔟 TOPIC RANKING FROM exam_summary
        # =====================================
        try:
            topic_query = """
                SELECT 
                    subject,
                    topic,
                    COUNT(*) as occurrence_count,
                    AVG(CAST(difficulty_score AS FLOAT)) as avg_difficulty,
                    MIN(CAST(difficulty_score AS FLOAT)) as min_difficulty,
                    MAX(CAST(difficulty_score AS FLOAT)) as max_difficulty,
                    MODE() WITHIN GROUP (ORDER BY difficulty_label) as most_common_label
                FROM exam_summary
                WHERE UPPER(exam) = UPPER(%s)
                    AND subject IS NOT NULL
                    AND topic IS NOT NULL
                GROUP BY subject, topic
                ORDER BY avg_difficulty DESC, occurrence_count DESC
            """
            
            topic_result = execute_query(topic_query, (db_exam,))
            logger.info(f"📊 Topic result: {len(topic_result) if topic_result else 0} rows")
            
            if topic_result and len(topic_result) > 0:
                hard_count = 0
                medium_count = 0
                easy_count = 0
                
                for row in topic_result:
                    score = float(row['avg_difficulty']) if row['avg_difficulty'] else 0
                    
                    # Use thresholds that match your data (3.0 for Hard, 2.0 for Medium)
                    if score >= 3.0:
                        level = "Hard"
                        hard_count += 1
                    elif score >= 2.0:
                        level = "Medium"
                        medium_count += 1
                    else:
                        level = "Easy"
                        easy_count += 1
                    
                    topic_rankings.append({
                        'subject': row['subject'],
                        'topic': row['topic'],
                        'avg_difficulty': score,
                        'occurrence_count': row['occurrence_count'],
                        'min_difficulty': float(row['min_difficulty']) if row['min_difficulty'] else score,
                        'max_difficulty': float(row['max_difficulty']) if row['max_difficulty'] else score,
                        'most_common_label': row['most_common_label'],
                        'level': level
                    })
                    
                    # For DifficultTopics component
                    topics_for_component.append({
                        'subject': row['subject'],
                        'topic': row['topic'],
                        'fused_difficulty_score': score,
                        'difficulty': score,
                        'level': level,
                        'occurrences': row['occurrence_count'],
                        'confidence': 0.85,
                        'difficulty_label': row['most_common_label'],
                        'tweets': 0,
                        'memes': 0,
                        'papers': 0
                    })
                
                logger.info(f"✅ Topic distribution - Hard: {hard_count}, Medium: {medium_count}, Easy: {easy_count}")
                logger.info(f"✅ Total topics: {len(topics_for_component)}")
                
            else:
                logger.warning(f"No topics found")
        except Exception as e:
            logger.error(f"Topic error: {e}")

        # =====================================
        # 1️⃣1️⃣ TOP 3 HARDEST/EASIEST
        # =====================================
        if len(topics_for_component) > 0:
            sorted_topics = sorted(topics_for_component, key=lambda x: x['difficulty'], reverse=True)
            top3_hardest = sorted_topics[:3]
            top3_easiest = sorted_topics[-3:] if len(sorted_topics) >= 3 else sorted_topics
            most_difficult_topics = sorted_topics[:10]

        # =====================================
        # 1️⃣2️⃣ DIFFICULTY DISTRIBUTION
        # =====================================
        if len(topics_for_component) > 0:
            hard_count = len([t for t in topics_for_component if t['level'] == 'Hard'])
            medium_count = len([t for t in topics_for_component if t['level'] == 'Medium'])
            easy_count = len([t for t in topics_for_component if t['level'] == 'Easy'])
            total = len(topics_for_component)
            
            difficulty_distribution = {
                'hard': hard_count,
                'medium': medium_count,
                'easy': easy_count,
                'total': total,
                'hard_pct': round(hard_count / total * 100, 1) if total > 0 else 0,
                'medium_pct': round(medium_count / total * 100, 1) if total > 0 else 0,
                'easy_pct': round(easy_count / total * 100, 1) if total > 0 else 0
            }
            
            logger.info(f"📊 Difficulty distribution - Hard: {hard_count}, Medium: {medium_count}, Easy: {easy_count}")

        # =====================================
        # 1️⃣3️⃣ TOPICS WITH HIGH OCCURRENCE
        # =====================================
        topics_over_100 = [t for t in topics_for_component if t['occurrences'] > 100]
        logger.info(f"📈 Topics with >100 occurrences: {len(topics_over_100)}")

        # =====================================
        # 1️⃣4️⃣ AI RECOMMENDATIONS
        # =====================================
        if len(topics_for_component) > 0:
            sorted_for_ai = sorted(topics_for_component, key=lambda x: (x['difficulty'], x['occurrences']), reverse=True)
            for i, topic in enumerate(sorted_for_ai[:5]):
                ai_recommendations.append({
                    'rank': i + 1,
                    'subject': topic['subject'],
                    'topic': topic['topic'],
                    'difficulty': topic['difficulty'],
                    'reason': f"Difficulty {topic['difficulty']} appears {topic['occurrences']} times",
                    'occurrences': topic['occurrences']
                })

        # =====================================
        # FINAL RESPONSE
        # =====================================
        response_data = {
            # Tweet data
            'tweet_stats': tweet_stats,
            'tweet_trend': tweet_trend_data,
            'tweet_yearly': tweet_trend_data,
            
            # Meme data
            'meme_stats': meme_stats,
            'meme_trend': meme_trend_data,
            'meme_yearly': meme_trend_data,
            'meme_count_by_year': meme_count_by_year,
            'yearly_stress_distribution': yearly_stress_distribution,
            
            # Subject and Topic data
            'subject_comparison': subject_comparison,
            'topic_rankings': topic_rankings,
            'topics': topics_for_component,
            'topics_over_100': topics_over_100,
            'top3_hardest': top3_hardest,
            'top3_easiest': top3_easiest,
            'most_difficult_topics': most_difficult_topics,
            'difficulty_distribution': difficulty_distribution,
            'ai_recommendations': ai_recommendations,
            'difficulty_classification': difficulty_classification,
            
            # Year-wise data
            'year_difficulty': year_difficulty_data,
            'stress_distribution_pie': stress_distribution_pie
        }

        # Final logs
        logger.info(f"✅ FINAL RESPONSE SUMMARY:")
        logger.info(f"   - Subjects: {len(subject_comparison)}")
        logger.info(f"   - Topics for component: {len(topics_for_component)}")
        logger.info(f"   - Topic rankings: {len(topic_rankings)}")
        logger.info(f"   - AI recommendations: {len(ai_recommendations)}")

        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in student_dashboard: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
        
# Helper functions for fallback data
def get_tweet_stats_from_knowledgegraph(exam):
    query = """
    SELECT 
        SUM(tweet_count) as tweet_count,
        AVG(tweet_stress_avg) as overall_stress,
        SUM(CASE WHEN tweet_stress_avg >= 3.5 THEN tweet_count ELSE 0 END) as high_stress,
        SUM(CASE WHEN tweet_stress_avg >= 2 AND tweet_stress_avg < 3.5 THEN tweet_count ELSE 0 END) as medium_stress,
        SUM(CASE WHEN tweet_stress_avg < 2 THEN tweet_count ELSE 0 END) as low_stress,
        COUNT(DISTINCT topic) as topic_count,
        AVG(difficulty_score) as avg_difficulty
    FROM knowledgegraph
    WHERE UPPER(exam) = UPPER(%s)
    """
    result = execute_query(query, (exam,))
    if result and len(result) > 0:
        data = result[0]
        total = data['tweet_count'] or 0
        
        return {
            'tweet_count': total,
            'overall_stress': round(float(data['overall_stress'] or 0), 1),
            'high_stress': data['high_stress'] or 0,
            'medium_stress': data['medium_stress'] or 0,
            'low_stress': data['low_stress'] or 0,
            'high_stress_pct': round((data['high_stress'] or 0) / total * 100, 1) if total > 0 else 0,
            'medium_stress_pct': round((data['medium_stress'] or 0) / total * 100, 1) if total > 0 else 0,
            'low_stress_pct': round((data['low_stress'] or 0) / total * 100, 1) if total > 0 else 0,
            'positive_sentiment': data['low_stress'] or 0,
            'negative_sentiment': data['high_stress'] or 0,
            'neutral_sentiment': data['medium_stress'] or 0,
            'positive_pct': round((data['low_stress'] or 0) / total * 100, 1) if total > 0 else 0,
            'negative_pct': round((data['high_stress'] or 0) / total * 100, 1) if total > 0 else 0,
            'neutral_pct': round((data['medium_stress'] or 0) / total * 100, 1) if total > 0 else 0,
            'avg_difficulty': round(float(data['avg_difficulty'] or 0), 2),
            'topic_count': data['topic_count'] or 0
        }
    return {}

def get_meme_stats_from_knowledgegraph(exam):
    query = """
    SELECT 
        SUM(meme_count) as meme_count,
        AVG(meme_stress_avg) as overall_stress,
        AVG(meme_sarcasm_score) as avg_sarcasm,
        SUM(CASE WHEN meme_is_sarcastic = true THEN meme_count ELSE 0 END) as sarcastic_count,
        SUM(CASE WHEN meme_stress_avg >= 3.5 THEN meme_count ELSE 0 END) as high_stress,
        SUM(CASE WHEN meme_stress_avg >= 2 AND meme_stress_avg < 3.5 THEN meme_count ELSE 0 END) as medium_stress,
        SUM(CASE WHEN meme_stress_avg < 2 THEN meme_count ELSE 0 END) as low_stress
    FROM knowledgegraph
    WHERE UPPER(exam) = UPPER(%s)
    """
    result = execute_query(query, (exam,))
    if result and len(result) > 0:
        data = result[0]
        total = data['meme_count'] or 0
        sarcastic = data['sarcastic_count'] or 0
        
        return {
            'meme_count': total,
            'avg_stress': round(float(data['overall_stress'] or 0), 1),
            'avg_sarcasm': round(float(data['avg_sarcasm'] or 0), 1),
            'sarcastic_count': sarcastic,
            'nonsarcastic_count': total - sarcastic,
            'sarcastic_pct': round(sarcastic / total * 100, 1) if total > 0 else 0,
            'high_stress': data['high_stress'] or 0,
            'medium_stress': data['medium_stress'] or 0,
            'low_stress': data['low_stress'] or 0,
            'high_stress_pct': round((data['high_stress'] or 0) / total * 100, 1) if total > 0 else 0,
            'medium_stress_pct': round((data['medium_stress'] or 0) / total * 100, 1) if total > 0 else 0,
            'low_stress_pct': round((data['low_stress'] or 0) / total * 100, 1) if total > 0 else 0
        }
    return {}

# TEACHER REGISTRATION API (Similar to Student)
# =============================================
@app.route('/api/teacher/register', methods=['POST', 'OPTIONS'])
def teacher_register():
    """Register teacher details - Matches student register pattern"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        data = request.json
        logger.info(f"Teacher registration data: {data}")
        
        # Extract teacher data
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        qualification = data.get('qualification')
        specialization = data.get('specialization')
        experience = data.get('experience')
        institute = data.get('institute')
        
        # Store in session (same as student)
        session['user_type'] = 'teacher'
        session['user_data'] = data
        
        # You could save to database here if needed
        # conn = get_db_connection()
        # cur = conn.cursor()
        return jsonify({
            'success': True,
            'message': 'Teacher registration successful',
            'data': data,
            'teacher_id': 1  # Return ID if saved to DB
        })
        
    except Exception as e:
        logger.error(f"Teacher registration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Add this helper function to get all distinct exams
def get_all_exams():
    """Get all distinct exams from relevant tables"""
    exams = set()
    
    queries = [
        "SELECT DISTINCT exam FROM exam_summary WHERE exam IS NOT NULL",
        "SELECT DISTINCT exam FROM topic_summary WHERE exam IS NOT NULL",
        "SELECT DISTINCT exam FROM year_summary WHERE exam IS NOT NULL",
        "SELECT DISTINCT node_name FROM kg_nodes WHERE node_type = 'root'"
    ]
    
    for query in queries:
        result = execute_query(query)
        if result:
            for row in result:
                if row and row.get('exam'):
                    exams.add(row['exam'])
                elif row and row.get('node_name'):
                    exams.add(row['node_name'])
    
    return sorted(list(exams))

# =============================================
# TEACHER DASHBOARD API - BASE ROUTE (NO EXAM PARAMETER)
# =============================================
@app.route('/api/teacher/dashboard', methods=['GET'])
@app.route('/api/teacher/dashboard/', methods=['GET'])
def teacher_dashboard_base():
    """Get teacher dashboard data for all exams"""
    return teacher_dashboard_with_exam('all')

# =============================================
# TEACHER DASHBOARD API - WITH EXAM PARAMETER
# =============================================
@app.route('/api/teacher/dashboard/<exam>', methods=['GET'])
def teacher_dashboard_with_exam(exam):
    """Get teacher dashboard data with exam-specific analytics"""
    try:
        exam_upper = exam.upper() if exam and exam != 'all' else None
        logger.info(f"Fetching teacher dashboard data for exam: {exam if exam else 'ALL'}")

        # Get all available exams for the filter dropdown
        def get_all_exams():
            """Get all distinct exams from relevant tables"""
            exams = set()
            
            queries = [
                "SELECT DISTINCT exam FROM exam_summary WHERE exam IS NOT NULL",
                "SELECT DISTINCT exam FROM topic_summary WHERE exam IS NOT NULL",
                "SELECT DISTINCT exam FROM year_summary WHERE exam IS NOT NULL",
                "SELECT DISTINCT node_name FROM kg_nodes WHERE node_type = 'root'"
            ]
            
            for query in queries:
                result = execute_query(query)
                if result:
                    for row in result:
                        if row and row.get('exam'):
                            exams.add(row['exam'])
                        elif row and row.get('node_name'):
                            exams.add(row['node_name'])
            
            return sorted(list(exams))

        available_exams = get_all_exams()
        logger.info(f"Available exams: {available_exams}")

        # =============================================
        # 1. TOPIC-WISE SUMMARY FROM topic_summary AND exam_summary
        # =============================================
        if exam_upper and exam_upper != 'ALL':
            topic_summary_query = """
                SELECT 
                    COALESCE(ts.subject, es.subject) as subject,
                    COALESCE(ts.topic, es.topic) as topic,
                    COALESCE(ts.occurrences, 1) as occurrences,
                    COALESCE(ts.total_tweets, 0) as tweet_count,
                    COALESCE(ts.avg_tweet_stress, 0) as tweet_stress,
                    COALESCE(ts.total_memes, 0) as meme_count,
                    COALESCE(ts.avg_meme_stress, 0) as meme_stress,
                    COALESCE(ts.total_papers, 0) as paper_count,
                    COALESCE(ts.avg_paper_difficulty, 0) as paper_difficulty,
                    COALESCE(ts.avg_fused_difficulty, es.difficulty_score, 0) as overall_difficulty,
                    es.difficulty_label,
                    es.confidence,
                    ts.exam
                FROM topic_summary ts
                FULL OUTER JOIN exam_summary es ON ts.exam = es.exam AND ts.subject = es.subject AND ts.topic = es.topic
                WHERE UPPER(COALESCE(ts.exam, es.exam)) = UPPER(%s)
                ORDER BY overall_difficulty DESC, occurrences DESC
            """
            topic_data = execute_query(topic_summary_query, (exam_upper,))
        else:
            topic_summary_query = """
                SELECT 
                    COALESCE(ts.subject, es.subject) as subject,
                    COALESCE(ts.topic, es.topic) as topic,
                    COALESCE(ts.occurrences, 1) as occurrences,
                    COALESCE(ts.total_tweets, 0) as tweet_count,
                    COALESCE(ts.avg_tweet_stress, 0) as tweet_stress,
                    COALESCE(ts.total_memes, 0) as meme_count,
                    COALESCE(ts.avg_meme_stress, 0) as meme_stress,
                    COALESCE(ts.total_papers, 0) as paper_count,
                    COALESCE(ts.avg_paper_difficulty, 0) as paper_difficulty,
                    COALESCE(ts.avg_fused_difficulty, es.difficulty_score, 0) as overall_difficulty,
                    es.difficulty_label,
                    
                    es.confidence,
                    ts.exam
                FROM topic_summary ts
                FULL OUTER JOIN exam_summary es ON ts.exam = es.exam AND ts.subject = es.subject AND ts.topic = es.topic
                WHERE COALESCE(ts.subject, es.subject) IS NOT NULL 
                  AND COALESCE(ts.topic, es.topic) IS NOT NULL
                ORDER BY overall_difficulty DESC, occurrences DESC
            """
            topic_data = execute_query(topic_summary_query)
        
        logger.info(f"Topic summary data: {len(topic_data) if topic_data else 0} rows")

        # =============================================
        # 2. YEAR-WISE SUMMARY FROM year_summary - FIXED
        # =============================================
        if exam_upper and exam_upper != 'ALL':
            year_summary_query = """
                SELECT 
                    year,
                    exam,
                    subjects_covered,
                    topics_covered,
                    total_entries,
                    avg_tweet_stress,
                    avg_meme_stress,
                    avg_paper_difficulty,
                    avg_fused_difficulty
                FROM year_summary
                WHERE UPPER(exam) = UPPER(%s)
                  AND year BETWEEN 2020 AND 2026
                ORDER BY year
            """
            year_data = execute_query(year_summary_query, (exam_upper,))
        else:
            year_summary_query = """
                SELECT 
                    year,
                    exam,
                    subjects_covered,
                    topics_covered,
                    total_entries,
                    avg_tweet_stress,
                    avg_meme_stress,
                    avg_paper_difficulty,
                    avg_fused_difficulty
                FROM year_summary
                WHERE year BETWEEN 2020 AND 2026
                ORDER BY year
            """
            year_data = execute_query(year_summary_query)
        
        logger.info(f"Year summary data: {len(year_data) if year_data else 0} rows")

        # Aggregate by year for charts
        year_aggregated = {}
        if year_data:
            for row in year_data:
                year = row['year']
                if year not in year_aggregated:
                    year_aggregated[year] = {
                        'year': year,
                        'tweet_stress': [],
                        'meme_stress': [],
                        'paper_difficulty': [],
                        'fused_difficulty': [],
                        'total_entries': 0,
                        'exams': set()
                    }
                year_aggregated[year]['tweet_stress'].append(float(row['avg_tweet_stress'] or 0))
                year_aggregated[year]['meme_stress'].append(float(row['avg_meme_stress'] or 0))
                year_aggregated[year]['paper_difficulty'].append(float(row['avg_paper_difficulty'] or 0))
                year_aggregated[year]['fused_difficulty'].append(float(row['avg_fused_difficulty'] or 0))
                year_aggregated[year]['total_entries'] += (row['total_entries'] or 0)
                year_aggregated[year]['exams'].add(row['exam'])

        year_chart_data = []
        for year, data in sorted(year_aggregated.items()):
            year_chart_data.append({
                'year': str(year),
                'tweet_stress': round(sum(data['tweet_stress']) / len(data['tweet_stress']), 2) if data['tweet_stress'] else 0,
                'meme_stress': round(sum(data['meme_stress']) / len(data['meme_stress']), 2) if data['meme_stress'] else 0,
                'paper_difficulty': round(sum(data['paper_difficulty']) / len(data['paper_difficulty']), 2) if data['paper_difficulty'] else 0,
                'fused_difficulty': round(sum(data['fused_difficulty']) / len(data['fused_difficulty']), 2) if data['fused_difficulty'] else 0,
                'total_entries': data['total_entries'],
                'exam_count': len(data['exams'])
            })

        # =============================================
        # 3. DECISION TREE DATA FROM kg_nodes
        # =============================================
        if exam_upper and exam_upper != 'ALL':
            root_query = """
                SELECT 
                    node_name,
                    node_type,
                    topic_count,
                    avg_difficulty,
                    overall_score,
                    exam
                FROM kg_nodes
                WHERE node_type = 'root' AND UPPER(node_name) = UPPER(%s)
                ORDER BY overall_score DESC
            """
            root_result = execute_query(root_query, (exam_upper,))
        else:
            root_query = """
                SELECT 
                    node_name,
                    node_type,
                    topic_count,
                    avg_difficulty,
                    overall_score,
                    exam
                FROM kg_nodes
                WHERE node_type = 'root'
                ORDER BY overall_score DESC
            """
            root_result = execute_query(root_query)
        
        logger.info(f"Root nodes: {len(root_result) if root_result else 0}")
        
        # Build tree structure
        tree_structure = {
            'name': 'Knowledge Graph',
            'children': []
        }
        
        if root_result:
            for root in root_result:
                exam_node = {
                    'name': root['node_name'],
                    'type': 'exam',
                    'topic_count': root['topic_count'],
                    'avg_difficulty': round(float(root['avg_difficulty'] or 0), 2),
                    'overall_score': round(float(root['overall_score'] or 0), 2),
                    'children': []
                }
                
                # Get subjects for this exam
                subject_query = """
                    SELECT 
                        node_name,
                        node_type,
                        topic_count,
                        avg_difficulty,
                        overall_score
                    FROM kg_nodes
                    WHERE node_type = 'subject' AND parent_node = %s
                    ORDER BY overall_score DESC
                """
                subject_result = execute_query(subject_query, (root['node_name'],))
                
                if subject_result:
                    for subject in subject_result:
                        subject_node = {
                            'name': subject['node_name'],
                            'type': 'subject',
                            'topic_count': subject['topic_count'],
                            'avg_difficulty': round(float(subject['avg_difficulty'] or 0), 2),
                            'overall_score': round(float(subject['overall_score'] or 0), 2),
                            'children': []
                        }
                        
                        # Get topics for this subject
                        topic_query = """
                            SELECT 
                                node_name,
                                node_type,
                                topic_count,
                                avg_difficulty,
                                overall_score
                            FROM kg_nodes
                            WHERE node_type = 'topic' AND parent_node = %s
                            ORDER BY overall_score DESC
                        """
                        topic_result = execute_query(topic_query, (subject['node_name'],))
                        
                        if topic_result:
                            for topic in topic_result:
                                score = float(topic['overall_score'] or 0)
                                topic_node = {
                                    'name': topic['node_name'],
                                    'type': 'topic',
                                    'topic_count': topic['topic_count'],
                                    'avg_difficulty': round(float(topic['avg_difficulty'] or 0), 2),
                                    'overall_score': round(score, 2),
                                    'difficulty_level': 'Hard' if score >= 3.0 else 
                                                       'Medium' if score >= 2.0 else 'Easy'
                                }
                                subject_node['children'].append(topic_node)
                        
                        exam_node['children'].append(subject_node)
                
                tree_structure['children'].append(exam_node)

        # =============================================
        # 4. KNOWLEDGE GRAPH STATS (with exam filter)
        # =============================================
        if exam_upper and exam_upper != 'ALL':
            kg_stats_query = """
                SELECT 
                    COUNT(DISTINCT CASE WHEN node_type = 'root' THEN node_name END) as total_exams,
                    COUNT(DISTINCT CASE WHEN node_type = 'subject' THEN node_name END) as total_subjects,
                    COUNT(DISTINCT CASE WHEN node_type = 'topic' THEN node_name END) as total_topics,
                    COUNT(*) as total_nodes,
                    AVG(overall_score) as avg_difficulty
                FROM kg_nodes
                WHERE UPPER(exam) = UPPER(%s) OR UPPER(node_name) = UPPER(%s)
            """
            kg_stats = execute_query(kg_stats_query, (exam_upper, exam_upper))
            
            edge_query = """
                SELECT 
                    parent.node_name as source,
                    child.node_name as target,
                    child.node_type as relationship,
                    child.overall_score as weight
                FROM kg_nodes child
                JOIN kg_nodes parent ON child.parent_node = parent.node_name
                WHERE child.node_type IN ('subject', 'topic')
                  AND (UPPER(parent.exam) = UPPER(%s) OR UPPER(child.exam) = UPPER(%s))
                ORDER BY child.overall_score DESC
            """
            edge_data = execute_query(edge_query, (exam_upper, exam_upper))
        else:
            kg_stats_query = """
                SELECT 
                    COUNT(DISTINCT CASE WHEN node_type = 'root' THEN node_name END) as total_exams,
                    COUNT(DISTINCT CASE WHEN node_type = 'subject' THEN node_name END) as total_subjects,
                    COUNT(DISTINCT CASE WHEN node_type = 'topic' THEN node_name END) as total_topics,
                    COUNT(*) as total_nodes,
                    AVG(overall_score) as avg_difficulty
                FROM kg_nodes
            """
            kg_stats = execute_query(kg_stats_query)
            
            edge_query = """
                SELECT 
                    parent.node_name as source,
                    child.node_name as target,
                    child.node_type as relationship,
                    child.overall_score as weight
                FROM kg_nodes child
                JOIN kg_nodes parent ON child.parent_node = parent.node_name
                WHERE child.node_type IN ('subject', 'topic')
                ORDER BY child.overall_score DESC
            """
            edge_data = execute_query(edge_query)

        # =============================================
        # 5. DIFFICULTY DISTRIBUTION (with exam filter and 3.0 threshold)
        # =============================================
        if exam_upper and exam_upper != 'ALL':
            difficulty_dist_query = """
                SELECT 
                    CASE 
                        WHEN overall_score >= 3.0 THEN 'Hard'
                        WHEN overall_score >= 2.0 THEN 'Medium'
                        ELSE 'Easy'
                    END as difficulty_level,
                    COUNT(*) as count,
                    node_type
                FROM kg_nodes
                WHERE overall_score IS NOT NULL
                  AND UPPER(exam) = UPPER(%s)
                GROUP BY 
                    CASE 
                        WHEN overall_score >= 3.0 THEN 'Hard'
                        WHEN overall_score >= 2.0 THEN 'Medium'
                        ELSE 'Easy'
                    END, 
                    node_type
            """
            difficulty_distribution = execute_query(difficulty_dist_query, (exam_upper,))
        else:
            difficulty_dist_query = """
                SELECT 
                    CASE 
                        WHEN overall_score >= 3.0 THEN 'Hard'
                        WHEN overall_score >= 2.0 THEN 'Medium'
                        ELSE 'Easy'
                    END as difficulty_level,
                    COUNT(*) as count,
                    node_type
                FROM kg_nodes
                WHERE overall_score IS NOT NULL
                GROUP BY 
                    CASE 
                        WHEN overall_score >= 3.0 THEN 'Hard'
                        WHEN overall_score >= 2.0 THEN 'Medium'
                        ELSE 'Easy'
                    END, 
                    node_type
            """
            difficulty_distribution = execute_query(difficulty_dist_query)

        # Sort in Python
        if difficulty_distribution:
            level_order = {'Hard': 1, 'Medium': 2, 'Easy': 3}
            difficulty_distribution.sort(key=lambda x: (level_order[x['difficulty_level']], x['node_type']))

        # =============================================
        # FINAL RESPONSE
        # =============================================
        response_data = {
            'topic_summary': topic_data if topic_data else [],
            'year_summary': year_data if year_data else [],
            'year_chart_data': year_chart_data,
            'tree_structure': tree_structure,
            'kg_stats': kg_stats[0] if kg_stats else {},
            'edge_data': edge_data if edge_data else [],
            'difficulty_distribution': difficulty_distribution if difficulty_distribution else [],
            'available_exams': available_exams,
            'selected_exam': exam if exam else 'all'
        }
        
        logger.info(f"✅ Teacher dashboard data retrieved successfully for exam: {exam if exam else 'ALL'}")
        logger.info(f"   - Topics: {len(topic_data) if topic_data else 0}")
        logger.info(f"   - Years: {len(year_chart_data)}")
        logger.info(f"   - Tree nodes: {kg_stats[0]['total_nodes'] if kg_stats else 0}")
        logger.info(f"   - Available exams: {len(available_exams)}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in teacher_dashboard: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Debug endpoints
@app.route('/api/debug/exams', methods=['GET'])
def debug_exams():
    try:
        queries = [
            "SELECT DISTINCT exam FROM analytics_tweets_exam WHERE exam IS NOT NULL",
            "SELECT DISTINCT exam FROM analytics_memes_exam WHERE exam IS NOT NULL",
            "SELECT DISTINCT exam FROM exam_summary WHERE exam IS NOT NULL",
            "SELECT DISTINCT exam FROM topic_summary WHERE exam IS NOT NULL"
        ]
        all_exams = set()
        for query in queries:
            results = execute_query(query)
            for row in results:
                if row and row.get('exam'):
                    all_exams.add(row['exam'])
        return jsonify({'available_exams': sorted(list(all_exams)) if all_exams else []})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'available_exams': ['JEE', 'NEET', 'GATE', 'TNPSC', 'UPSC', 'UGC NET']})

# -----------------------------
# API: COURSES LIST
# -----------------------------
@app.route('/api/courses', methods=['GET', 'OPTIONS'])
def api_courses():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    courses = {
        'school': ['10th', '11th', '12th'],
        'bachelor': [
            'B.Sc Computer Science', 'B.Sc Mathematics', 'B.Sc Physics', 
            'B.Sc Chemistry', 'B.Sc Biology', 'B.Sc Electronics',
            'B.A Economics', 'B.A History', 'B.A Political Science',
            'B.Com', 'B.B.A', 'B.C.A'
        ],
        'master': [
            'M.Sc Computer Science', 'M.Sc Mathematics', 'M.Sc Physics',
            'M.Sc Chemistry', 'M.Sc Biology', 'M.A Economics',
            'M.Com', 'M.C.A', 'M.B.A'
        ]
    }
    return jsonify(courses)

# -----------------------------
# API: MAJORS LIST
# -----------------------------
@app.route('/api/majors', methods=['GET', 'OPTIONS'])
def api_majors():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    majors = {
        'Computer Science': ['Algorithms', 'Data Structures', 'Programming', 'Database', 'Networks', 'AI', 'ML'],
        'Mathematics': ['Calculus', 'Algebra', 'Geometry', 'Statistics', 'Probability', 'Trigonometry'],
        'Physics': ['Mechanics', 'Thermodynamics', 'Optics', 'Quantum', 'Electromagnetism', 'Relativity'],
        'Chemistry': ['Organic', 'Inorganic', 'Physical', 'Analytical', 'Polymer', 'Biochemistry'],
        'Biology': ['Botany', 'Zoology', 'Cell Biology', 'Genetics', 'Ecology', 'Microbiology'],
        'Economics': ['Microeconomics', 'Macroeconomics', 'Econometrics', 'Development', 'International'],
        'History': ['Ancient', 'Medieval', 'Modern', 'World History', 'Indian History'],
        'Political Science': ['Political Theory', 'International Relations', 'Public Administration'],
        'Commerce': ['Accounting', 'Finance', 'Marketing', 'HR', 'Taxation']
    }
    return jsonify(majors)


# -----------------------------
# API: TNPSC GROUPS
# -----------------------------
@app.route('/api/tnpsc-groups', methods=['GET', 'OPTIONS'])
def api_tnpsc_groups():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    groups = ['Group 1', 'Group 2', 'Group 2A', 'Group 3', 'Group 4']
    return jsonify(groups)


# -----------------------------
# API: EXAM TYPES
# -----------------------------
@app.route('/api/exam-types', methods=['GET', 'OPTIONS'])
def api_exam_types():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    exam_types = ['School', 'Bachelor', 'Master', 'Competitive']
    return jsonify(exam_types)


# -----------------------------
# API: EXAMS
# -----------------------------
@app.route('/api/exams', methods=['GET', 'OPTIONS'])
def api_exams():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    exam_type = request.args.get('type', '')
    
    exams = {
        'School': ['10th Board', '12th Board'],
        'Bachelor': ['University Exams', 'Semester Exams'],
        'Master': ['University Exams', 'Semester Exams'],
        'Competitive': ['JEE', 'NEET', 'GATE', 'CAT', 'UPSC', 'TNPSC', 'SSC', 'Banking','UGC NET']
    }
    
    return jsonify(exams.get(exam_type, []))


# -----------------------------
# API: SPECIALIZATIONS
# -----------------------------
@app.route('/api/specializations', methods=['GET', 'OPTIONS'])
def api_specializations():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    course = request.args.get('course', '')
    
    specializations = {
        'B.Sc Computer Science': ['Programming', 'Web Development', 'Database', 'Networks'],
        'B.Sc Mathematics': ['Pure Mathematics', 'Applied Mathematics', 'Statistics'],
        'B.Sc Physics': ['Quantum Physics', 'Nuclear Physics', 'Astrophysics'],
        'B.Sc Chemistry': ['Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry'],
        'B.Sc Biology': ['Botany', 'Zoology', 'Microbiology', 'Genetics'],
        'M.Sc Computer Science': ['Advanced Programming', 'Machine Learning', 'Data Science'],
        'M.C.A': ['Software Development', 'System Programming', 'Cloud Computing'],
        'B.Com': ['Accounting', 'Finance', 'Taxation', 'Auditing'],
        'B.B.A': ['Marketing', 'Finance', 'HR', 'Operations']
    }
    
    return jsonify(specializations.get(course, []))


# -----------------------------
# API: DEBUG EXAMS
# -----------------------------
@app.route('/api/debug/exams', methods=['GET', 'OPTIONS'])
def api_debug_exams():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        queries = [
            "SELECT DISTINCT exam FROM analytics_tweets WHERE exam IS NOT NULL",
            "SELECT DISTINCT exam FROM analytics_memes WHERE exam IS NOT NULL",
            "SELECT DISTINCT exam FROM knowledge_graph WHERE exam IS NOT NULL"
        ]
        all_exams = set()
        for query in queries:
            results = execute_query(query)
            for row in results:
                if row and row.get('exam'):
                    all_exams.add(row['exam'])
        return jsonify({'available_exams': sorted(list(all_exams)) if all_exams else ['JEE', 'NEET', 'TNPSC']})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'available_exams': ['JEE', 'NEET', 'TNPSC']})


# -----------------------------
# API: HEALTH CHECK
# -----------------------------
@app.route('/api/health', methods=['GET', 'OPTIONS'])
def api_health():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    return jsonify({'status': 'healthy'})


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    logger.info("Starting Flask server on port 5000...")
    app.run(debug=True, port=5000, host='0.0.0.0')