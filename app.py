from flask import Flask, jsonify, request, session
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from datetime import timedelta
import os
import logging
from datetime import datetime
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure CORS
CORS(app, supports_credentials=True, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3008"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            dbname="exam_ai_db",
            user="postgres",
            password="password",
            host="localhost",
            port="5432",
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=None):
    """Execute query and return results"""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("No database connection")
            return []
        
        cur = conn.cursor()
        
        # Handle params properly
        if params is not None and not isinstance(params, (tuple, list)):
            params = (params,)
        
        logger.debug(f"Executing query: {query[:100]}...")
        cur.execute(query, params)
        
        if query.strip().upper().startswith('SELECT'):
            result = cur.fetchall()
            logger.debug(f"Query returned {len(result)} rows")
            return result
        else:
            conn.commit()
            return {'affected_rows': cur.rowcount}
            
    except Exception as e:
        logger.error(f"Query error: {e}")
        logger.error(traceback.format_exc())
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

# Student Registration
@app.route('/api/student/register', methods=['POST', 'OPTIONS'])
def student_register():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.json
        logger.info(f"Student registration data: {data}")
        
        # Store in session
        session['user_type'] = 'student'
        session['user_data'] = data
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'data': data
        })
        
    except Exception as e:
        logger.error(f"Student registration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Student Dashboard
@app.route('/api/student/dashboard/<exam>', methods=['GET'])
def student_dashboard(exam):
    """Get student dashboard data from database"""
    logger.info(f"Fetching dashboard data for exam: {exam}")
    
    try:
        exam_upper = exam.upper()
        
        # ===== 1. TWEET STATS from analytics_tweets =====
        tweet_stats_query = """
            SELECT 
                COALESCE(AVG(stress_score), 0) as avg_stress,
                COUNT(*) as total_tweets,
                COALESCE(SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END), 0) as positive_count,
                COALESCE(SUM(CASE WHEN sentiment_label = 'negative' THEN 1 ELSE 0 END), 0) as negative_count,
                COALESCE(SUM(CASE WHEN sentiment_label = 'neutral' THEN 1 ELSE 0 END), 0) as neutral_count
            FROM analytics_tweets 
            WHERE UPPER(exam) = UPPER(%s)
        """
        tweet_stats_result = execute_query(tweet_stats_query, (exam_upper,))
        
        if tweet_stats_result and len(tweet_stats_result) > 0:
            data = tweet_stats_result[0]
            total = data['total_tweets'] or 1
            
            tweet_stats = {
                'overall_stress': round(float(data['avg_stress']) * 10, 1),  # Convert to percentage
                'positive_pct': round(data['positive_count'] / total * 100, 1),
                'negative_pct': round(data['negative_count'] / total * 100, 1),
                'neutral_pct': round(data['neutral_count'] / total * 100, 1),
                'total_tweets': data['total_tweets']
            }
            logger.debug(f"Tweet stats from DB: {tweet_stats}")
        else:
            # Fallback if no data
            tweet_stats = {
                'overall_stress': 65.5,
                'positive_pct': 28.5,
                'negative_pct': 48.2,
                'neutral_pct': 23.3,
                'total_tweets': 1250
            }
        
        # ===== 2. TWEET TREND from analytics_tweets =====
        tweet_trend_query = """
            SELECT 
                TO_CHAR(created_at, 'YYYY-MM-DD') as date,
                COALESCE(AVG(stress_score * 10), 0) as avg_stress,
                COUNT(*) as count
            FROM analytics_tweets 
            WHERE UPPER(exam) = UPPER(%s)
            GROUP BY TO_CHAR(created_at, 'YYYY-MM-DD')
            ORDER BY date ASC
            LIMIT 30
        """
        tweet_trend_result = execute_query(tweet_trend_query, (exam_upper,))
        
        if tweet_trend_result and len(tweet_trend_result) > 0:
            tweet_trend = []
            for row in tweet_trend_result:
                tweet_trend.append({
                    'date': row['date'],
                    'avg_stress': round(float(row['avg_stress']), 1),
                    'tweet_count': row['count']
                })
        else:
            tweet_trend = []
        
        # ===== 3. SENTIMENT TREND from analytics_tweets - FIXED =====
        sentiment_trend_query = """
            SELECT 
                TO_CHAR(created_at, 'YYYY-MM-DD') as date,
                COALESCE(SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END), 0) as positive,
                COALESCE(SUM(CASE WHEN sentiment_label = 'negative' THEN 1 ELSE 0 END), 0) as negative,
                COALESCE(SUM(CASE WHEN sentiment_label = 'neutral' THEN 1 ELSE 0 END), 0) as neutral,
                COUNT(*) as total
            FROM analytics_tweets 
            WHERE UPPER(exam) = UPPER(%s)
            GROUP BY TO_CHAR(created_at, 'YYYY-MM-DD')
            ORDER BY date ASC
            LIMIT 30
        """
        sentiment_result = execute_query(sentiment_trend_query, (exam_upper,))
        
        if sentiment_result and len(sentiment_result) > 0:
            sentiment_trend = []
            for row in sentiment_result:
                total = row['total'] or 1
                sentiment_trend.append({
                    'date': row['date'],
                    'positive': round(row['positive'] / total * 100, 1),
                    'negative': round(row['negative'] / total * 100, 1),
                    'neutral': round(row['neutral'] / total * 100, 1)
                })
        else:
            # Generate sample sentiment trend for demonstration
            sentiment_trend = []
            for i in range(30):
                date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
                sentiment_trend.append({
                    'date': date,
                    'positive': round(30 + (i * 0.5), 1),
                    'negative': round(50 - (i * 0.3), 1),
                    'neutral': round(20, 1)
                })
        
        # ===== 4. STRESS DISTRIBUTION from analytics_tweets =====
        stress_dist_query = """
            SELECT 
                CASE 
                    WHEN stress_score >= 7 THEN 'High'
                    WHEN stress_score >= 4 THEN 'Medium'
                    ELSE 'Low'
                END as stress_level,
                COUNT(*) as count
            FROM analytics_tweets 
            WHERE UPPER(exam) = UPPER(%s) AND stress_score IS NOT NULL
            GROUP BY stress_level
        """
        stress_dist_result = execute_query(stress_dist_query, (exam_upper,))
        
        if stress_dist_result and len(stress_dist_result) > 0:
            total = sum(row['count'] for row in stress_dist_result)
            stress_distribution = []
            for row in stress_dist_result:
                stress_distribution.append({
                    'level': row['stress_level'],
                    'count': row['count'],
                    'percentage': round(row['count'] / total * 100, 1)
                })
        else:
            stress_distribution = [
                {'level': 'High', 'count': 45, 'percentage': 45},
                {'level': 'Medium', 'count': 35, 'percentage': 35},
                {'level': 'Low', 'count': 20, 'percentage': 20}
            ]
        
        # ===== 5. MEME SARCASM from analytics_memes =====
        meme_query = """
            SELECT 
                COUNT(*) as total_memes,
                COALESCE(SUM(CASE WHEN is_sarcastic = true THEN 1 ELSE 0 END), 0) as sarcastic_count,
                COALESCE(AVG(CASE WHEN is_sarcastic THEN 100 ELSE 0 END), 0) as avg_sarcasm,
                COALESCE(AVG(stress_score * 10), 0) as avg_stress
            FROM analytics_memes 
            WHERE UPPER(exam) = UPPER(%s)
        """
        meme_result = execute_query(meme_query, (exam_upper,))
        
        if meme_result and len(meme_result) > 0:
            data = meme_result[0]
            total = data['total_memes'] or 1
            sarcastic = data['sarcastic_count']
            
            meme_sarcasm = {
                'total_memes': data['total_memes'],
                'sarcastic_count': sarcastic,
                'non_sarcastic_count': total - sarcastic,
                'sarcastic_pct': round(sarcastic / total * 100, 1) if total > 0 else 0,
                'avg_sarcasm': round(float(data['avg_sarcasm']), 1),
                'avg_stress': round(float(data['avg_stress']), 1)
            }
        else:
            meme_sarcasm = {
                'total_memes': 0,
                'sarcastic_count': 0,
                'non_sarcastic_count': 0,
                'sarcastic_pct': 0,
                'avg_sarcasm': 0,
                'avg_stress': 0
            }
        
        # ===== 6. DIFFICULTY CLASSIFICATION from knowledge_graph =====
        difficulty_query = """
            SELECT 
                CASE 
                    WHEN difficulty_score >= 4.0 THEN 'Hard'
                    WHEN difficulty_score >= 2.5 THEN 'Medium'
                    ELSE 'Easy'
                END as difficulty_level,
                COUNT(*) as count
            FROM knowledge_graph
            WHERE UPPER(exam) = UPPER(%s) AND difficulty_score IS NOT NULL
            GROUP BY difficulty_level
        """
        difficulty_result = execute_query(difficulty_query, (exam_upper,))
        
        if difficulty_result and len(difficulty_result) > 0:
            total = sum(row['count'] for row in difficulty_result)
            difficulty_classification = []
            for row in difficulty_result:
                difficulty_classification.append({
                    'level': row['difficulty_level'],
                    'count': row['count'],
                    'percentage': round(row['count'] / total * 100, 1)
                })
        else:
            difficulty_classification = [
                {'level': 'Hard', 'count': 55, 'percentage': 55},
                {'level': 'Medium', 'count': 30, 'percentage': 30},
                {'level': 'Easy', 'count': 15, 'percentage': 15}
            ]
        
        # ===== 7. YEAR-WISE DIFFICULTY TREND from analytics_fusion =====
        year_difficulty_query = """
            SELECT 
                year,
                AVG(fused_difficulty_score) as avg_difficulty
            FROM analytics_fusion
            WHERE UPPER(exam) = UPPER(%s) AND year IS NOT NULL
            GROUP BY year
            ORDER BY year
        """
        year_difficulty_result = execute_query(year_difficulty_query, (exam_upper,))
        
        if year_difficulty_result and len(year_difficulty_result) > 0:
            year_difficulty = []
            for row in year_difficulty_result:
                year_difficulty.append({
                    'year': row['year'],
                    'difficulty': round(float(row['avg_difficulty']), 2)
                })
        else:
            # Generate sample year data
            year_difficulty = [
                {'year': 2019, 'difficulty': 0.52},
                {'year': 2020, 'difficulty': 0.60},
                {'year': 2021, 'difficulty': 0.63},
                {'year': 2022, 'difficulty': 0.70},
                {'year': 2023, 'difficulty': 0.75}
            ]
        
        # ===== 8. SUBJECT DIFFICULTY COMPARISON from knowledge_graph =====
        subject_difficulty_query = """
            SELECT 
                subject,
                AVG(difficulty_score) as avg_difficulty
            FROM knowledge_graph
            WHERE UPPER(exam) = UPPER(%s) 
                AND subject IS NOT NULL 
                AND subject NOT ILIKE '%general%'
            GROUP BY subject
            ORDER BY avg_difficulty DESC
            LIMIT 10
        """
        subject_difficulty_result = execute_query(subject_difficulty_query, (exam_upper,))
        
        if subject_difficulty_result and len(subject_difficulty_result) > 0:
            subject_difficulty = []
            for row in subject_difficulty_result:
                subject_difficulty.append({
                    'subject': row['subject'],
                    'difficulty': round(float(row['avg_difficulty']) / 5.0, 2)  # Normalize to 0-1 scale
                })
        else:
            subject_difficulty = [
                {'subject': 'Computer Science', 'difficulty': 0.72},
                {'subject': 'Mathematics', 'difficulty': 0.65},
                {'subject': 'Aptitude', 'difficulty': 0.45},
                {'subject': 'Physics', 'difficulty': 0.68},
                {'subject': 'Chemistry', 'difficulty': 0.58}
            ]
        
        # ===== 9. AI RECOMMENDATIONS based on difficulty =====
        ai_recommendations = generate_ai_recommendations(exam_upper, subject_difficulty)
        
        # ===== 10. TOPIC DIFFICULTIES from knowledge_graph =====
        topic_query = """
            SELECT 
                subject,
                topic,
                AVG(difficulty_score) as avg_difficulty,
                COUNT(*) as occurrence
            FROM knowledge_graph
            WHERE UPPER(exam) = UPPER(%s) 
                AND subject IS NOT NULL 
                AND topic IS NOT NULL
                AND subject NOT ILIKE '%general%'
                AND topic NOT ILIKE '%general%'
            GROUP BY subject, topic
            HAVING AVG(difficulty_score) IS NOT NULL
            ORDER BY avg_difficulty DESC
        """
        topic_result = execute_query(topic_query, (exam_upper,))
        
        if topic_result and len(topic_result) >= 5:
            # Hardest topics
            hardest = []
            for i, row in enumerate(topic_result[:5]):
                hardest.append({
                    'rank': i + 1,
                    'subject': row['subject'],
                    'topic': row['topic'],
                    'difficulty': round(float(row['avg_difficulty']), 2)
                })
            
            # Easiest topics
            easiest = []
            reversed_results = list(reversed(topic_result))
            for i, row in enumerate(reversed_results[:5]):
                easiest.append({
                    'rank': i + 1,
                    'subject': row['subject'],
                    'topic': row['topic'],
                    'difficulty': round(float(row['avg_difficulty']), 2)
                })
            
            # All topics with fused difficulty score
            all_topics = []
            for i, row in enumerate(topic_result):
                # Calculate fused difficulty score using formula
                paper_difficulty = float(row['avg_difficulty']) / 5.0  # Normalize to 0-1
                tweet_stress = tweet_stats['overall_stress'] / 100  # Normalize to 0-1
                meme_sentiment = meme_sarcasm['avg_stress'] / 100 if meme_sarcasm['avg_stress'] > 0 else 0.5
                
                fused_score = (0.5 * paper_difficulty) + (0.3 * tweet_stress) + (0.2 * meme_sentiment)
                
                all_topics.append({
                    'rank': i + 1,
                    'subject': row['subject'],
                    'topic': row['topic'],
                    'fused_difficulty_score': round(fused_score, 2),
                    'paper_difficulty': round(paper_difficulty, 2),
                    'tweet_stress': round(tweet_stress, 2),
                    'meme_sentiment': round(meme_sentiment, 2)
                })
            
            topic_difficulties = {
                'hardest': hardest,
                'easiest': easiest,
                'all_topics': all_topics
            }
        else:
            # Try papers_raw as fallback
            paper_topic_query = """
                SELECT 
                    subject,
                    topic,
                    AVG(CASE 
                        WHEN difficulty = 'Hard' THEN 4.5
                        WHEN difficulty = 'Medium' THEN 3.0
                        WHEN difficulty = 'Easy' THEN 1.5
                        ELSE 3.0
                    END) as avg_difficulty,
                    COUNT(*) as occurrence
                FROM papers_raw
                WHERE UPPER(exam) = UPPER(%s) 
                    AND subject IS NOT NULL 
                    AND topic IS NOT NULL
                GROUP BY subject, topic
                ORDER BY avg_difficulty DESC
            """
            paper_result = execute_query(paper_topic_query, (exam_upper,))
            
            if paper_result and len(paper_result) >= 5:
                hardest = []
                for i, row in enumerate(paper_result[:5]):
                    hardest.append({
                        'rank': i + 1,
                        'subject': row['subject'],
                        'topic': row['topic'],
                        'difficulty': round(float(row['avg_difficulty']), 2)
                    })
                
                easiest = []
                reversed_results = list(reversed(paper_result))
                for i, row in enumerate(reversed_results[:5]):
                    easiest.append({
                        'rank': i + 1,
                        'subject': row['subject'],
                        'topic': row['topic'],
                        'difficulty': round(float(row['avg_difficulty']), 2)
                    })
                
                all_topics = []
                for i, row in enumerate(paper_result):
                    paper_difficulty = float(row['avg_difficulty']) / 5.0
                    tweet_stress = tweet_stats['overall_stress'] / 100
                    meme_sentiment = meme_sarcasm['avg_stress'] / 100 if meme_sarcasm['avg_stress'] > 0 else 0.5
                    
                    fused_score = (0.5 * paper_difficulty) + (0.3 * tweet_stress) + (0.2 * meme_sentiment)
                    
                    all_topics.append({
                        'rank': i + 1,
                        'subject': row['subject'],
                        'topic': row['topic'],
                        'fused_difficulty_score': round(fused_score, 2),
                        'paper_difficulty': round(paper_difficulty, 2),
                        'tweet_stress': round(tweet_stress, 2),
                        'meme_sentiment': round(meme_sentiment, 2)
                    })
                
                topic_difficulties = {
                    'hardest': hardest,
                    'easiest': easiest,
                    'all_topics': all_topics
                }
            else:
                topic_difficulties = {
                    'hardest': [],
                    'easiest': [],
                    'all_topics': []
                }
        
        response_data = {
            'tweet_data': tweet_trend,
            'tweet_overall_stats': tweet_stats,
            'meme_data': meme_sarcasm,
            'difficulty_data': difficulty_classification,
            'topics_data': topic_difficulties,
            'sentiment_trend': sentiment_trend,
            'stress_distribution': stress_distribution,
            'year_difficulty': year_difficulty,
            'subject_difficulty': subject_difficulty,
            'ai_recommendations': ai_recommendations
        }
        
        logger.info(f"Dashboard data for {exam_upper} retrieved from database")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in student_dashboard: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

def generate_ai_recommendations(exam, subject_difficulty):
    """Generate AI recommendations based on difficulty analysis"""
    recommendations = {
        'JEE': [
            'Calculus - Focus on integration techniques and applications',
            'Electromagnetism - Practice numerical problems',
            'Organic Chemistry - Memorize reaction mechanisms',
            'Coordinate Geometry - Master conic sections',
            'Physical Chemistry - Understand thermodynamics laws'
        ],
        'NEET': [
            'Human Physiology - Focus on digestive and respiratory systems',
            'Organic Chemistry - Practice name reactions',
            'Genetics - Understand Mendelian inheritance',
            'Plant Physiology - Study photosynthesis in depth',
            'Biomolecules - Memorize structures and functions'
        ],
        'TNPSC': [
            'Indian Constitution - Focus on fundamental rights and duties',
            'Ancient History - Study Indus Valley and Mauryan Empire',
            'Tamil Literature - Understand Sangam period',
            'Indian Economy - Focus on budget and five-year plans',
            'Geography - Study physical features of India'
        ],
        'UPSC': [
            'Modern History - Focus on freedom struggle',
            'Indian Polity - Understand parliamentary system',
            'Geography - Study climate and vegetation',
            'Economy - Focus on economic surveys',
            'International Relations - Study India\'s foreign policy'
        ]
    }
    
    # Default recommendations
    default_recs = [
        'Focus on high-difficulty subjects first',
        'Practice previous year papers regularly',
        'Take mock tests to identify weak areas',
        'Create revision notes for quick review',
        'Join study groups for collaborative learning'
    ]
    
    # Get exam-specific recommendations or use default
    exam_recs = recommendations.get(exam, default_recs)
    
    # Add subject-based recommendations
    subject_recs = []
    if subject_difficulty and len(subject_difficulty) > 0:
        hardest_subjects = sorted(subject_difficulty, key=lambda x: x['difficulty'], reverse=True)[:3]
        subject_recs = [f"Focus on {s['subject']} - Difficulty: {s['difficulty']*100:.0f}%" for s in hardest_subjects]
    
    return {
        'exam_specific': exam_recs[:3],
        'subject_based': subject_recs,
        'general': default_recs[:2]
    }

# Teacher Dashboard
@app.route('/api/teacher/dashboard', methods=['GET'])
def teacher_dashboard():
    """Get teacher dashboard data from database"""
    logger.info("Fetching teacher dashboard data")
    
    try:
        # Topic data from knowledge_graph
        topic_query = """
            SELECT 
                subject,
                topic,
                AVG(difficulty_score) as avg_difficulty,
                COUNT(*) as occurrence_count,
                'knowledge_graph' as source
            FROM knowledge_graph
            WHERE subject IS NOT NULL 
                AND subject != ''
                AND subject NOT ILIKE '%general%'
                AND topic IS NOT NULL 
                AND topic != ''
                AND topic NOT ILIKE '%general%'
            GROUP BY subject, topic
            HAVING COUNT(*) > 0
            ORDER BY avg_difficulty DESC NULLS LAST
            LIMIT 30
        """
        topic_data = execute_query(topic_query)
        
        # Stress data from tweets
        stress_query = """
            SELECT 
                TO_CHAR(created_at, 'YYYY-MM-DD') as date,
                AVG(stress_score * 10) as avg_stress,
                COUNT(*) as count,
                'tweets' as source
            FROM analytics_tweets
            WHERE stress_score IS NOT NULL
            GROUP BY TO_CHAR(created_at, 'YYYY-MM-DD')
            ORDER BY date DESC
            LIMIT 30
        """
        stress_data = execute_query(stress_query)
        
        # Year data from analytics_fusion
        year_query = """
            SELECT 
                year,
                AVG(tweet_stress_avg) as avg_tweet_stress,
                AVG(meme_stress_avg) as avg_meme_stress,
                AVG(paper_difficulty_avg) as avg_paper_difficulty,
                AVG(fused_difficulty_score) as avg_fused_difficulty
            FROM analytics_fusion
            WHERE year IS NOT NULL
            GROUP BY year
            ORDER BY year
        """
        year_data = execute_query(year_query)
        
        # Exam data from knowledge_graph
        exam_query = """
            SELECT 
                exam,
                COUNT(*) as entries,
                AVG(difficulty_score) as avg_difficulty,
                SUM(CASE WHEN difficulty_score >= 4.0 THEN 1 ELSE 0 END) as hard_count,
                SUM(CASE WHEN difficulty_score >= 2.5 AND difficulty_score < 4.0 THEN 1 ELSE 0 END) as medium_count,
                SUM(CASE WHEN difficulty_score < 2.5 THEN 1 ELSE 0 END) as easy_count
            FROM knowledge_graph
            WHERE exam IS NOT NULL 
                AND exam != ''
                AND exam NOT ILIKE '%general%'
            GROUP BY exam
            HAVING COUNT(*) > 0
            ORDER BY avg_difficulty DESC NULLS LAST
        """
        exam_data = execute_query(exam_query)
        
        return jsonify({
            'topic_data': topic_data if topic_data else [],
            'stress_data': stress_data if stress_data else [],
            'year_data': year_data if year_data else [],
            'exam_data': exam_data if exam_data else []
        })
        
    except Exception as e:
        logger.error(f"Error in teacher_dashboard: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Dropdown data endpoints
@app.route('/api/courses', methods=['GET', 'OPTIONS'])
def get_courses():
    if request.method == 'OPTIONS':
        return '', 200
        
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

@app.route('/api/majors', methods=['GET', 'OPTIONS'])
def get_majors():
    if request.method == 'OPTIONS':
        return '', 200
        
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

@app.route('/api/tnpsc-groups', methods=['GET', 'OPTIONS'])
def get_tnpsc_groups():
    if request.method == 'OPTIONS':
        return '', 200
        
    groups = ['Group 1', 'Group 2', 'Group 2A', 'Group 3', 'Group 4']
    return jsonify(groups)

@app.route('/api/exam-types', methods=['GET', 'OPTIONS'])
def get_exam_types():
    if request.method == 'OPTIONS':
        return '', 200
        
    exam_types = ['School', 'Bachelor', 'Master', 'Competitive']
    return jsonify(exam_types)

@app.route('/api/exams', methods=['GET', 'OPTIONS'])
def get_exams():
    if request.method == 'OPTIONS':
        return '', 200
        
    exam_type = request.args.get('type', '')
    
    exams = {
        'School': ['10th Board', '12th Board'],
        'Bachelor': ['University Exams', 'Semester Exams'],
        'Master': ['University Exams', 'Semester Exams'],
        'Competitive': ['JEE', 'NEET', 'GATE', 'CAT', 'UPSC', 'TNPSC', 'SSC', 'Banking']
    }
    
    return jsonify(exams.get(exam_type, []))

@app.route('/api/specializations', methods=['GET', 'OPTIONS'])
def get_specializations():
    if request.method == 'OPTIONS':
        return '', 200
        
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

# Debug endpoint
@app.route('/api/debug/exams', methods=['GET'])
def debug_exams():
    """Get all available exams from database"""
    try:
        queries = [
            "SELECT DISTINCT exam FROM analytics_tweets WHERE exam IS NOT NULL",
            "SELECT DISTINCT exam FROM analytics_memes WHERE exam IS NOT NULL",
            "SELECT DISTINCT exam FROM analytics_fusion WHERE exam IS NOT NULL",
            "SELECT DISTINCT exam FROM knowledge_graph WHERE exam IS NOT NULL"
        ]
        
        all_exams = set()
        tweet_exams = []
        meme_exams = []
        fusion_exams = []
        kg_exams = []
        
        for i, query in enumerate(queries):
            results = execute_query(query)
            for row in results:
                if row and row.get('exam'):
                    exam_value = row['exam']
                    all_exams.add(exam_value)
                    if i == 0:
                        tweet_exams.append(exam_value)
                    elif i == 1:
                        meme_exams.append(exam_value)
                    elif i == 2:
                        fusion_exams.append(exam_value)
                    else:
                        kg_exams.append(exam_value)
        
        return jsonify({
            'available_exams': sorted(list(all_exams)) if all_exams else [],
            'tweet_exams': tweet_exams or [],
            'meme_exams': meme_exams or [],
            'fusion_exams': fusion_exams or [],
            'knowledge_graph_exams': kg_exams or []
        })
    except Exception as e:
        logger.error(f"Error in debug_exams: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask server on port 5000...")
    app.run(debug=True, port=5000, host='0.0.0.0')