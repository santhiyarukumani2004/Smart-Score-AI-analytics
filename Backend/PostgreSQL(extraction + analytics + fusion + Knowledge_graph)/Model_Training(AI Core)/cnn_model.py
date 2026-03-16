import psycopg2
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import re

# ===============================
# MODEL
device = "cuda" if torch.cuda.is_available() else "cpu"

model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
model = nn.Sequential(*list(model.children())[:-1])
model.eval().to(device)

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485,0.456,0.406],
        std=[0.229,0.224,0.225]
    )
])

# ===============================
# TEXT & EMOJI LOGIC
EMOJI_REGEX = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]+")

STRESS_WORDS = [
    "fail","pressure","stress","panic","tension","fear",
    "rank","cutoff","result","exam","marks"
]

SARCASM_WORDS = [
    "lol","haha","yeah right","as if","sure","great"
]

EXAM_KEYWORDS = {
    "NEET": ["neet","medical","mbbs"],
    "JEE": ["jee","iit","engineering"],
    "NET": ["ugc","assistant professor","net exam"],
    "TNPSC": ["tnpsc","group","govt job"]
}

HEADERS = {"User-Agent":"Mozilla/5.0"}

# ===============================
def detect_exam(text):
    text = text.lower()
    for exam, keys in EXAM_KEYWORDS.items():
        if any(k in text for k in keys):
            return exam
    return None

def text_stress_score(text):
    return sum(1 for w in STRESS_WORDS if w in text.lower())

def is_sarcastic_text(text):
    return any(w in text.lower() for w in SARCASM_WORDS)

def load_image(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if "image" not in r.headers.get("Content-Type",""):
            return None
        return Image.open(BytesIO(r.content)).convert("RGB")
    except:
        return None

# ===============================
# DATABASE
conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

cur.execute("""
SELECT id, image_url, ocr_text, final_text, emojis
FROM memes_raw
""")

memes = cur.fetchall()
print(f"📥 Processing {len(memes)} memes")

inserted = 0
skipped = 0

# ===============================
for meme_id, image_url, ocr_text, final_text, emojis in memes:

    combined_text = f"{ocr_text or ''} {final_text or ''}".strip()

    # ---- EXAM DETECTION WITH FALLBACK ----
    exam = detect_exam(combined_text)

    text_score = text_stress_score(combined_text)
    emoji_score = len(EMOJI_REGEX.findall(emojis or ""))

    if exam is None:
        if text_score >= 2 or emoji_score >= 2:
            exam = "GENERAL_EXAM"
        else:
            skipped += 1
            continue

    # ---- IMAGE OPTIONAL ----
    img = load_image(image_url)
    visual_score = 0.0

    if img:
        img_tensor = transform(img).unsqueeze(0).to(device)
        with torch.no_grad():
            features = model(img_tensor).squeeze().cpu().numpy()
        visual_score = np.linalg.norm(features) / 1200

    # ---- FINAL STRESS SCORE ----
    stress_score = int(min(
        (visual_score * 0.4) +
        (text_score * 0.4) +
        (emoji_score * 0.2),
        1.0
    ) * 100)

    # ---- LEVEL ----
    if stress_score >= 70:
        stress_level = "high"
        difficulty = "hard"
    elif stress_score >= 40:
        stress_level = "medium"
        difficulty = "medium"
    else:
        stress_level = "low"
        difficulty = "low"

    is_stress = stress_score >= 40
    sarcastic = is_sarcastic_text(combined_text) or emoji_score >= 3

    if sarcastic:
        emotion = "Sarcasm"
    elif stress_level == "high":
        emotion = "Frustration"
    elif stress_level == "medium":
        emotion = "Anxiety"
    else:
        emotion = "Neutral"

    cur.execute("""
    INSERT INTO analytics_memes_new (
        meme_id, exam,
        stress_score, stress_level, is_stress,
        emoji_score, is_sarcastic,
        emotional_label, difficulty_signal
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        meme_id, exam,
        stress_score, stress_level, is_stress,
        emoji_score, sarcastic,
        emotion, difficulty
    ))

    inserted += 1

conn.commit()
cur.close()
conn.close()

print("=================================")
print(f"✅ SUCCESS: {inserted} memes analyzed and stored")
print(f"⚠️ Skipped (low signal): {skipped}")
