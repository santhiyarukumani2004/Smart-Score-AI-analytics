import os
import re
import cv2
import pytesseract
import pandas as pd

# -----------------------------
# CONFIGURATION
# -----------------------------
IMAGE_ROOT = "images/JEE"        # images/NEET-2023/page_1.png ...
OUTPUT_CSV = "output/jee_questions.csv"

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
        shift = "Unknown"

    return year, shift

# -----------------------------
# OCR FUNCTION
# -----------------------------
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
        "rough page"
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

    # -----------------------------
    # JEE MATHEMATICS TOPICS
    # -----------------------------
    MATHEMATICS = {
        "Algebra": [
            "quadratic", "polynomial", "equation", "roots",
            "complex number", "sequence", "series",
            "binomial", "permutation", "combination",
            "determinant", "matrix", "rank"
        ],

        "Trigonometry": [
            "trigonometry", "sin", "cos", "tan",
            "cosec", "sec", "cot",
            "trigonometric identity",
            "inverse trigonometric"
        ],

        "Coordinate Geometry": [
            "straight line", "pair of lines",
            "circle", "parabola", "ellipse", "hyperbola",
            "focus", "directrix", "latus rectum"
        ],

        "Calculus - Limits & Continuity": [
            "limit", "continuity", "differentiability"
        ],

        "Calculus - Differentiation": [
            "derivative", "differentiate",
            "rate of change", "slope",
            "maxima", "minima", "tangent", "normal"
        ],

        "Calculus - Integration": [
            "integration", "integral",
            "definite integral", "indefinite integral",
            "area under curve"
        ],

        "Calculus - Differential Equations": [
            "differential equation", "order", "degree"
        ],

        "Vector & 3D Geometry": [
            "vector", "dot product", "cross product",
            "scalar triple product",
            "line in space", "plane",
            "direction cosine", "direction ratio"
        ],

        "Probability & Statistics": [
            "probability", "random variable",
            "mean", "variance", "standard deviation",
            "binomial distribution"
        ]
    }

    # -----------------------------
    # JEE PHYSICS TOPICS
    # -----------------------------
    PHYSICS = {
        "Mechanics": [
            "motion", "velocity", "acceleration",
            "force", "newton", "work", "energy",
            "power", "collision", "gravitation"
        ],

        "Thermodynamics": [
            "thermodynamics", "heat", "temperature",
            "entropy", "first law", "second law"
        ],

        "Electrostatics": [
            "charge", "electric field",
            "coulomb", "potential", "capacitor"
        ],

        "Current Electricity": [
            "current", "voltage", "resistance",
            "ohm", "kirchhoff", "wheatstone"
        ],

        "Magnetism & EMI": [
            "magnetic field", "magnetic force",
            "electromagnetic induction",
            "faraday", "lenz"
        ],

        "Optics": [
            "reflection", "refraction",
            "lens", "mirror", "interference",
            "diffraction", "polarization"
        ],

        "Modern Physics": [
            "photoelectric", "bohr",
            "radioactivity", "nuclear",
            "semiconductor", "diode", "transistor"
        ]
    }

    # -----------------------------
    # JEE CHEMISTRY TOPICS
    # -----------------------------
    CHEMISTRY = {
        "Physical Chemistry": [
            "mole", "stoichiometry", "thermodynamics",
            "equilibrium", "electrochemistry",
            "kinetics", "solution", "solid state"
        ],

        "Organic Chemistry": [
            "alkane", "alkene", "alkyne",
            "benzene", "alcohol", "phenol",
            "aldehyde", "ketone", "carboxylic",
            "amine", "polymer"
        ],

        "Inorganic Chemistry": [
            "periodic table", "coordination",
            "metallurgy", "p block", "d block",
            "s block", "salt analysis"
        ]
    }

    # -----------------------------
    # CLASSIFICATION ORDER
    # -----------------------------
    for topic, keys in MATHEMATICS.items():
        if any(k in q for k in keys):
            return "Mathematics", topic

    for topic, keys in PHYSICS.items():
        if any(k in q for k in keys):
            return "Physics", topic

    for topic, keys in CHEMISTRY.items():
        if any(k in q for k in keys):
            return "Chemistry", topic

    return "Unknown", "Unknown"

# Enhanced version with weighted scoring for better accuracy
def classify_subject_topic_advanced(q, threshold=2):
    """
    Advanced classification with weighted scoring to handle overlapping keywords
    Args:
        q: Question text string
        threshold: Minimum keyword matches required
    Returns:
        tuple: (subject, topic)
    """
    q = q.lower()
    
    # Define dictionaries (same as above)
    BIOLOGY = {...}  # Same as above
    PHYSICS = {...}   # Same as above
    CHEMISTRY = {...} # Same as above
    
    subject_scores = {"Biology": 0, "Physics": 0, "Chemistry": 0}
    topic_scores = {}
    
    # Score BIOLOGY
    for topic, keys in BIOLOGY.items():
        matches = sum(1 for k in keys if k in q)
        if matches > 0:
            subject_scores["Biology"] += matches
            topic_scores[topic] = matches
    
    # Score PHYSICS
    for topic, keys in PHYSICS.items():
        matches = sum(1 for k in keys if k in q)
        if matches > 0:
            subject_scores["Physics"] += matches
            topic_scores[topic] = matches
    
    # Score CHEMISTRY
    for topic, keys in CHEMISTRY.items():
        matches = sum(1 for k in keys if k in q)
        if matches > 0:
            subject_scores["Chemistry"] += matches
            topic_scores[topic] = matches
    
    # Determine subject with highest score
    if max(subject_scores.values()) >= threshold:
        subject = max(subject_scores, key=subject_scores.get)
        # Get the specific topic within that subject
        subject_topics = {}
        
        if subject == "Biology":
            subject_dict = BIOLOGY
        elif subject == "Physics":
            subject_dict = PHYSICS
        else:
            subject_dict = CHEMISTRY
        
        for topic, keys in subject_dict.items():
            matches = sum(1 for k in keys if k in q)
            if matches > 0:
                subject_topics[topic] = matches
        
        if subject_topics:
            topic = max(subject_topics, key=subject_topics.get)
            return subject, topic
    
    return "Unknown", "Unknown"


# -----------------------------
# BLOOM LEVEL
# -----------------------------
def bloom_level(q):
    q = q.lower()
    if any(w in q for w in ["define", "identify"]):
        return "Remember"
    if any(w in q for w in ["explain", "describe"]):
        return "Understand"
    if any(w in q for w in ["calculate", "determine"]):
        return "Apply"
    if any(w in q for w in ["analyze", "compare"]):
        return "Analyze"
    return "Understand"

# -----------------------------
# DIFFICULTY
# -----------------------------
def difficulty(q):
    n = len(q.split())
    if n < 20:
        return "Easy"
    elif n < 35:
        return "Medium"
    else:
        return "Hard"

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
                    "exam": "JEE",
                    "year": year,
                    "shift": shift,
                    "question_text": q,
                    "question_length": len(q.split()),
                    "subject": subject,
                    "topic": topic,
                    "bloom_level": bloom_level(q),
                    "difficulty": difficulty(q)
                })

df = pd.DataFrame(rows)
df.to_csv(OUTPUT_CSV, index=False)

print("✅ CSV CREATED:", OUTPUT_CSV)
