import os
import re
import cv2
import pytesseract
import pandas as pd

IMAGE_ROOT = "images/tnpsc"
OUTPUT_CSV = "output/tnpsc_questions.csv"

pytesseract.pytesseract.tesseract_cmd = r"E:\Program Files\Tesseract-OCR\tesseract.exe"

os.makedirs("output", exist_ok=True)

def parse_year_shift(folder_name):
    """
    Extracts year and shift from folder name like:
    jee-2023(shift1)
    """
    folder_name = folder_name.lower()
    # year
    year_match = re.search(r"(20\d{2})", folder_name)
    year = year_match.group(1) if year_match else "Unknown"
    # shift
    shift_match = re.search(r"\(shift\s*(\d)\)", folder_name)
    if shift_match:
        shift = f"Shift {shift_match.group(1)}"
    else:
        shift = "No"

    return year, shift

def ocr_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return pytesseract.image_to_string(gray, lang="eng")

# -----------------------------
# TEXT CLEANING
# -----------------------------
def remove_instructions(text):
    patterns = [
        r"Test Booklet Code.*?Important Instructions:",
        r"Important Instructions:.*?Section B shall consist",
        r"The test is of.*?single correct answer\)",
         "important instructions",
        "test booklet",
        "answer sheet",
        "do not open",
        "duration",
        "rough page",
        "total questions",
        "total marks",
        "instructions to candidates",
        "use of calculator",
        "use of mobile phone",
        "write your roll number",
        "write your registration number",
        "write your test booklet code",
        "this question paper contains",
        "please read the instructions carefully",
        "marks for each question",
        "negative marking",
        "all questions are compulsory",
        "marks will be deducted for wrong answers",
        "no marks will be awarded for unattempted questions",
        "do not write anything on this question paper",
        "use only blue or black ball point pen",
        "use of pencil is not allowed",
        "this is a computer based test",
        "the use of unfair means is strictly prohibited",
        "maximum marks",
        "total duration",
        "number of questions",        "section a",
        "section b",        "section c"        ,        "section d",
        "end of the question paper",
        "page \d+ of \d+",
        "question paper",
    ]
    for p in patterns:
        text = re.sub(p, "", text, flags=re.DOTALL | re.IGNORECASE)
    return text

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[|_—]+', ' ', text)
    return text.strip()

# -----------------------------
# QUESTION SPLITTING
# -----------------------------
def split_questions(text):
    questions = re.split(r'(?<=\s)\d{1,3}\.\s', text)
    return [q.strip() for q in questions if len(q.split()) > 10]

def classify_subject_topic(q):
    q = q.lower()

    TNPSC_GS = {
        "History": {
            "keywords": [
                "indus valley", "harappa", "vedic", "maurya", "gupta", "mughal",
                "freedom struggle", "indian national congress", "british rule",
                "revolt of 1857", "chola", "pandya", "pallava", "chera",
                "temple architecture", "inscriptions", "ashoka", "akbar",
                "shivaji", "vijayanagara", "buddhism", "jainism",
                "delhi sultanate", "sangam age", "medieval india",
                "ancient india", "modern india", "world war", "renaissance",
                "french revolution", "industrial revolution"
            ],
            "sub_topics": [
                "Ancient History", "Medieval History", "Modern History",
                "World History", "Tamil Nadu History", "Freedom Struggle",
                "Cultural History", "Archaeology"
            ]
        },

        "Geography": {
            "keywords": [
                "latitude", "longitude", "monsoon", "climate", "soil", "river",
                "delta", "mountain", "plateau", "plain", "natural vegetation",
                "mineral", "population", "agriculture", "industries",
                "resources", "ocean", "atmosphere", "weather", "earthquake",
                "volcano", "tsunami", "cyclone", "drainage", "environment",
                "biosphere", "conservation", "wildlife", "national park",
                "sanctuary"
            ],
            "sub_topics": [
                "Physical Geography", "Human Geography", "Indian Geography",
                "World Geography", "Economic Geography", "Environmental Geography",
                "Climatology", "Oceanography"
            ]
        },

        "Indian Polity": {
            "keywords": [
                "constitution", "preamble", "fundamental rights",
                "fundamental duties", "directive principles", "parliament",
                "president", "prime minister", "supreme court", "high court",
                "election commission", "governor", "chief minister",
                "local self government", "panchayat", "municipality",
                "union executive", "state executive", "judiciary",
                "constitutional bodies", "non-constitutional bodies",
                "amendment", "emergency", "citizenship", "union territories"
            ],
            "sub_topics": [
                "Constitution of India", "Central Government", "State Government",
                "Local Government", "Judicial System", "Constitutional Bodies",
                "Electoral System", "Indian Federalism"
            ]
        },

        "Indian Economy": {
            "keywords": [
                "gdp", "inflation", "deflation", "budget", "tax", "gst",
                "planning commission", "niti aayog", "poverty", "unemployment",
                "banking", "rbi", "monetary policy", "fiscal policy",
                "five year plan", "economic survey", "demographic dividend",
                "foreign trade", "balance of payment", "currency", "stock market",
                "insurance", "sebi", "disinvestment", "privatization",
                "liberalization", "globalization", "agricultural economy"
            ],
            "sub_topics": [
                "Macroeconomics", "Microeconomics", "Public Finance",
                "Banking & Finance", "International Trade", "Economic Planning",
                "Agricultural Economy", "Industrial Economy"
            ]
        },

        "Science & Technology": {
            "keywords": [
                "physics", "chemistry", "biology", "atom", "molecule", "cell",
                "human body", "digestive system", "blood", "disease", "vaccine",
                "photosynthesis", "environment", "ecosystem", "pollution",
                "renewable energy", "computer", "internet", "mobile", "satellite",
                "space", "nuclear", "defense", "biotechnology", "nanotechnology",
                "artificial intelligence", "robotics", "genetics", "evolution"
            ],
            "sub_topics": [
                "Physics", "Chemistry", "Biology", "Environmental Science",
                "Information Technology", "Space Technology", "Defense Technology",
                "Medical Science", "Agricultural Science"
            ]
        },

        "Current Affairs": {
            "keywords": [
                "recent", "latest", "current", "scheme", "policy", "summit",
                "award", "sports", "conference", "census", "report",
                "government initiative", "budget", "economic survey",
                "international relations", "sports event", "books and authors",
                "important days", "persons in news", "places in news",
                "science and technology news"
            ],
            "sub_topics": [
                "National Current Affairs", "International Current Affairs",
                "Sports", "Awards & Honors", "Government Schemes",
                "Economic Developments", "Scientific Developments"
            ]
        },

        "Tamil Nadu Studies": {
            "keywords": [
                "tamil nadu", "tn government", "samacheer kalvi",
                "veeramamunivar", "thiruvalluvar", "sangam", "tirukkural",
                "dravidian movement", "tn budget", "tn scheme", "river cauvery",
                "chennai", "madurai", "coimbatore", "tamil literature",
                "tamil language", "tamil culture", "tamil cinema", "tamil music",
                "tamil architecture", "tamil cuisine", "folk arts",
                "classical dance", "temple festivals", "local governance",
                "tn economy", "tn industries", "tn agriculture", "tn tourism"
            ],
            "sub_topics": [
                "Tamil Language & Literature", "Tamil Culture & Heritage",
                "Tamil Nadu Geography", "Tamil Nadu Economy",
                "Tamil Nadu Politics", "Tamil Nadu Administration",
                "Tamil Nadu Tourism", "Tamil Nadu Education"
            ]
        },

        "General Knowledge": {
            "keywords": [
                "first in india", "largest", "smallest", "highest", "lowest",
                "longest", "shortest", "abbreviation", "full form",
                "important dates", "national symbols", "capitals", "currencies",
                "important books", "authors", "inventions", "discoveries",
                "sports trophies", "art and culture", "dance forms",
                "music instruments", "festivals", "religions", "languages"
            ],
            "sub_topics": [
                "First in India/World", "Books & Authors", "Sports",
                "Awards & Honors", "Countries & Capitals",
                "Important Dates & Days", "Art & Culture", "Miscellaneous"
            ]
        },

        "Reasoning & Mental Ability": {
            "keywords": [
                "analogy", "classification", "series", "coding-decoding",
                "blood relation", "direction sense", "calendar", "clock",
                "venn diagram", "syllogism", "statement and conclusion",
                "logical reasoning", "mathematical operations", "puzzle",
                "seating arrangement", "missing number", "mirror image",
                "water image", "cube and dice", "non-verbal reasoning",
                "verbal reasoning", "analytical reasoning"
            ],
            "sub_topics": [
                "Verbal Reasoning", "Non-Verbal Reasoning", "Logical Deduction",
                "Analytical Reasoning", "Mathematical Reasoning",
                "Series Completion", "Classification", "Direction Sense"
            ]
        },

        "Mathematics": {
            "keywords": [
                "algebra", "geometry", "trigonometry", "calculus", "statistics",
                "probability", "arithmetic", "percentage", "ratio", "proportion",
                "profit and loss", "simple interest", "compound interest",
                "time and work", "time and distance", "average", "number system",
                "hcf", "lcm", "fraction", "decimal", "mensuration", "area",
                "volume", "permutation", "combination", "quadratic equation",
                "linear equation", "set theory", "matrices", "determinants"
            ],
            "sub_topics": [
                "Arithmetic", "Algebra", "Geometry", "Trigonometry",
                "Statistics & Probability", "Mensuration", "Number System",
                "Commercial Mathematics"
            ]
        },

        "English Language": {
            "keywords": [
                "grammar", "vocabulary", "comprehension", "synonym", "antonym",
                "one word substitute", "idioms", "phrases", "error detection",
                "sentence correction", "para jumbles", "cloze test",
                "reading comprehension", "preposition", "conjunction",
                "article", "tense", "voice", "narration", "degrees of comparison",
                "parts of speech", "sentence completion", "spelling check"
            ],
            "sub_topics": [
                "Grammar", "Vocabulary", "Comprehension", "Error Detection",
                "Sentence Correction", "Para Jumbles", "Idioms & Phrases",
                "One Word Substitution"
            ]
        }
    }

    for subject, data in TNPSC_GS.items():
        if any(k in q for k in data["keywords"]):
            # Find the most specific sub-topic
            for sub_topic in data["sub_topics"]:
                sub_topic_lower = sub_topic.lower()
                if any(keyword in q for keyword in sub_topic_lower.split()):
                    return subject, sub_topic
            return subject, data["sub_topics"][0]  # Default to first sub-topic
    
    return "General Studies", "General"

# BLOOM LEVEL
# -----------------------------
def bloom_level(q):
    q = q.lower()
    bloom_keywords = {
        "Remember": ["define", "identify", "list", "name", "recall", "state", "what is", "who was"],
        "Understand": ["explain", "describe", "summarize", "interpret", "paraphrase", "discuss", "how does"],
        "Apply": ["calculate", "determine", "solve", "use", "apply", "demonstrate", "show how", "compute"],
        "Analyze": ["analyze", "compare", "contrast", "differentiate", "distinguish", "examine", "investigate", "why"],
        "Evaluate": ["evaluate", "justify", "critique", "assess", "recommend", "argue", "defend", "judge"],
        "Create": ["design", "formulate", "plan", "create", "construct", "develop", "propose", "invent"]
    }
    
    for level, keywords in bloom_keywords.items():
        if any(keyword in q for keyword in keywords):
            return level
    
    return "Understand"  # Default level

# -----------------------------
# DIFFICULTY
# -----------------------------
def difficulty(q):
    n = len(q.split())
    if n < 15:
        return "Easy"
    elif n < 30:
        return "Medium"
    elif n < 50:
        return "Hard"
    else:
        return "Very Hard"

# -----------------------------
# MAIN PIPELINE
# -----------------------------
rows = []

for year_folder in os.listdir(IMAGE_ROOT):
    year = year_folder.split("-")[-1]
    folder_path = os.path.join(IMAGE_ROOT, year_folder)

    print(f"Processing {year_folder}...")
    year, shift = parse_year_shift(year_folder)
    print(f"Processing {year_folder} → Year: {year}, Shift: {shift}")
    
    for img_file in sorted(os.listdir(folder_path)):
        if img_file.endswith(".png"):
            image_path = os.path.join(folder_path, img_file)

            text = ocr_image(image_path)
            text = remove_instructions(text)
            text = clean_text(text)

            questions = split_questions(text)

            for q in questions:
                subject, topic = classify_subject_topic(q)
                rows.append({
                    "exam": "TNPSC",
                    "year": year,
                    "shift": shift,
                    "question_text": q,
                    "question_length": len(q.split()),
                    "subject": subject,
                    "topic": topic,
                    "bloom_level": bloom_level(q),
                    "difficulty": difficulty(q),
                    "image_source": img_file,
                    "folder_source": year_folder
                })

df = pd.DataFrame(rows)
df.to_csv(OUTPUT_CSV, index=False)

print("✅ CSV CREATED:", OUTPUT_CSV)
print(f"Total questions extracted: {len(rows)}")

# Additional analysis
if len(rows) > 0:
    print("\n📊 Subject-wise distribution:")
    subject_dist = df['subject'].value_counts()
    for subject, count in subject_dist.items():
        print(f"  {subject}: {count} questions ({count/len(rows)*100:.1f}%)")
    
    print("\n📊 Difficulty distribution:")
    difficulty_dist = df['difficulty'].value_counts()
    for difficulty, count in difficulty_dist.items():
        print(f"  {difficulty}: {count} questions")