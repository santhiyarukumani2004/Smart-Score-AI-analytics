import os
import re
import cv2
import pytesseract
import pandas as pd

IMAGE_ROOT = "images/GATE"
OUTPUT_CSV = "output/gate_cs_questions.csv"

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

    GATE_CS = {
        "Programming": [
            "c program", "pointer", "array", "structure",
            "recursion", "function", "malloc", "free"
        ],

        "Data Structures": [
            "stack", "queue", "linked list", "tree",
            "binary tree", "bst", "heap", "graph",
            "hashing", "priority queue"
        ],

        "Algorithms": [
            "time complexity", "space complexity",
            "big o", "big theta", "big omega",
            "dynamic programming", "greedy",
            "divide and conquer", "shortest path",
            "dijkstra", "bellman ford", "kruskal", "prim"
        ],

        "Operating Systems": [
            "process", "thread", "cpu scheduling",
            "deadlock", "semaphore", "mutex",
            "paging", "segmentation", "virtual memory",
            "page replacement", "disk scheduling"
        ],

        "Database Management Systems": [
            "sql", "query", "normalization",
            "functional dependency", "er model",
            "transaction", "acid", "serializability",
            "index", "b tree"
        ],

        "Computer Networks": [
            "osi", "tcp", "udp", "ip",
            "congestion control", "flow control",
            "routing", "arp", "dns", "http"
        ],

        "Theory of Computation": [
            "finite automata", "dfa", "nfa",
            "regular expression", "cfg",
            "pushdown automata", "turing machine",
            "decidability", "regular language"
        ],

        "Compiler Design": [
            "lexical analysis", "parser",
            "syntax tree", "first", "follow",
            "ll", "lr", "intermediate code",
            "code optimization"
        ],

        "Computer Organization": [
            "pipeline", "cache", "memory hierarchy",
            "instruction set", "risc", "cisc",
            "addressing mode", "cpu"
        ],

        "Discrete Mathematics": [
            "set theory", "relation", "function",
            "graph theory", "tree",
            "logic", "boolean algebra",
            "combinatorics", "recurrence"
        ]
    }

    for topic, keywords in GATE_CS.items():
        if any(k in q for k in keywords):
            return "Computer Science", topic

    return "Computer Science", "General"

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
                    "exam": "GATE",
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