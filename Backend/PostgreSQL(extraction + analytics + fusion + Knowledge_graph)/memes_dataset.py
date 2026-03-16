# memes_dataset_fixed.py
import psycopg2
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import re
from collections import Counter
import time

# ===============================
# CONFIGURATION
BATCH_SIZE = 50  # Process in batches to avoid memory issues
CACHE_DIR = "meme_cache"
import os
os.makedirs(CACHE_DIR, exist_ok=True)

# ===============================
# MODEL
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"📦 Using device: {device}")

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
# TEXT ANALYSIS
EXAM_KEYWORDS = {
    "NEET": ["neet","medical","mbbs","biology","doctor","aiims","medico"],
    "JEE": ["jee","iit","engineering","physics","maths","iitjee","jeemains"],
    "UPSC": ["upsc","ias","ips","civil service","cse","ifs"],
    "GATE": ["gate","cse","computer science","ece","mechanical"],
    "TNPSC": ["tnpsc","group","tamilnadu","government exam"],
    "UGC NET": ["ugc","net","assistant professor","jrf","phd"],
    "SSC": ["ssc","cgl","chsl","mts","staff selection"]
}

STRESS_WORDS = [
    "fail","pressure","stress","panic","tension","fear","rank","cutoff",
    "result","marks","tough","hard","difficult","anxiety","depressed",
    "cry","crying","sad","upset","worried","hopeless","burden","exhausted"
]

SARCASM_WORDS = [
    "lol","haha","yeah right","as if","great","sure","obviously",
    "🤣","😂","😏","🙄","😅", "sarcasm", "irony"
]

EMOJI_REGEX = re.compile(
    "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+"
)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ===============================
def detect_exam(text):
    """Detect exam from text, return 'GENERAL' if none found"""
    if not text:
        return "GENERAL"
    text = text.lower()
    for exam, keys in EXAM_KEYWORDS.items():
        if any(k in text for k in keys):
            return exam
    return "GENERAL"

def text_stress_score(text):
    """Calculate stress score from text"""
    if not text:
        return 0
    text = text.lower()
    return sum(1 for w in STRESS_WORDS if w in text)

def text_sarcasm_score(text):
    """Calculate sarcasm score from text"""
    if not text:
        return 0
    text = text.lower()
    return sum(2 for w in SARCASM_WORDS if w in text)

def is_sarcastic(text, emoji_count):
    """Determine if meme is sarcastic"""
    text_score = text_sarcasm_score(text)
    return (text_score > 0) or (emoji_count >= 2)

def load_image(url, meme_id):
    """Download image with caching"""
    try:
        # Create cache filename
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_path = os.path.join(CACHE_DIR, f"{url_hash}.jpg")
        
        # Return cached image if exists
        if os.path.exists(cache_path):
            return Image.open(cache_path).convert("RGB")
        
        # Download image
        r = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        if "image" not in r.headers.get("Content-Type", ""):
            return None
        
        # Save to cache
        with open(cache_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return Image.open(cache_path).convert("RGB")
    except Exception as e:
        print(f"⚠️ Image load failed for ID {meme_id}: {str(e)[:50]}")
        return None

def extract_emojis(emojis_text):
    """Extract and count emojis"""
    if not emojis_text:
        return 0, []
    found = EMOJI_REGEX.findall(str(emojis_text))
    return len(found), found

# ===============================
# DB CONNECTION
conn = psycopg2.connect(
    dbname="exam_ai_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Create analytics table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS analytics_memes_new (
    id SERIAL PRIMARY KEY,
    meme_id INT REFERENCES memes_raw(id) ON DELETE CASCADE,
    exam TEXT,
    stress_score INT,
    stress_level TEXT,
    is_stress BOOLEAN,
    emoji_score INT,
    is_sarcastic BOOLEAN,
    emotional_label TEXT,
    difficulty_signal TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(meme_id)
);
""")
conn.commit()

# Get memes with images
cur.execute("""
SELECT id, image_url, ocr_text, final_text, emojis
FROM memes_raw
WHERE image_url IS NOT NULL AND image_url != ''
ORDER BY id
""")

memes = cur.fetchall()
total_memes = len(memes)
print(f"📥 Found {total_memes} memes with images to process")

# Clear existing analytics for these memes
meme_ids = [m[0] for m in memes]
if meme_ids:
    cur.execute(
        "DELETE FROM analytics_memes_new WHERE meme_id = ANY(%s)",
        (meme_ids,)
    )
    conn.commit()
    print(f"🧹 Cleared {cur.rowcount} existing analytics records")

# ===============================
# PROCESS MEMES
inserted = 0
failed_images = 0
exam_counter = Counter()
stress_levels = Counter()

insert_query = """
INSERT INTO analytics_memes_new (
    meme_id, exam, stress_score, stress_level,
    is_stress, emoji_score, is_sarcastic,
    emotional_label, difficulty_signal
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (meme_id) DO UPDATE SET
    exam = EXCLUDED.exam,
    stress_score = EXCLUDED.stress_score,
    stress_level = EXCLUDED.stress_level,
    is_stress = EXCLUDED.is_stress,
    emoji_score = EXCLUDED.emoji_score,
    is_sarcastic = EXCLUDED.is_sarcastic,
    emotional_label = EXCLUDED.emotional_label,
    difficulty_signal = EXCLUDED.difficulty_signal,
    analyzed_at = CURRENT_TIMESTAMP
"""

print("\n🚀 Processing memes...")
print("-" * 60)

for idx, (meme_id, image_url, ocr_text, final_text, emojis) in enumerate(memes, 1):
    
    # Progress indicator
    if idx % 50 == 0 or idx == total_memes:
        print(f"📊 Progress: {idx}/{total_memes} (Success: {inserted}, Failed: {failed_images})")
    
    # Combine text
    combined_text = f"{ocr_text or ''} {final_text or ''}".strip()
    
    # Detect exam (will be GENERAL if none found)
    exam = detect_exam(combined_text)
    exam_counter[exam] += 1
    
    # Load image
    img = load_image(image_url, meme_id)
    if img is None:
        failed_images += 1
        # Still insert basic text-based analysis even if image fails
        emoji_count, emoji_list = extract_emojis(emojis)
        text_score_val = text_stress_score(combined_text)
        
        # Text-only analysis
        stress_score = min(text_score_val * 20, 100)
        
        if stress_score >= 70:
            stress_level = "high"
            difficulty = "hard"
            emotion = "Anxiety"
        elif stress_score >= 40:
            stress_level = "medium"
            difficulty = "medium"
            emotion = "Neutral"
        else:
            stress_level = "low"
            difficulty = "easy"
            emotion = "Neutral"
        
        sarcastic = is_sarcastic(combined_text, emoji_count)
        if sarcastic:
            emotion = "Sarcasm"
        
        try:
            cur.execute(insert_query, (
                meme_id, exam, stress_score, stress_level,
                stress_score >= 40, emoji_count, sarcastic,
                emotion, difficulty
            ))
            conn.commit()
            inserted += 1
        except Exception as e:
            print(f"❌ DB error for ID {meme_id}: {e}")
            conn.rollback()
        
        continue
    
    # Process with image
    try:
        # Transform image
        img_tensor = transform(img).unsqueeze(0).to(device)
        
        # Extract features
        with torch.no_grad():
            features = model(img_tensor).squeeze().cpu().numpy()
        
        # -------- VISUAL SCORE --------
        visual_score = min(np.linalg.norm(features) / 1000, 1.0)
        
        # -------- TEXT SCORE --------
        text_score_val = text_stress_score(combined_text)
        text_score = min(text_score_val / 5, 1.0)
        
        # -------- EMOJI SCORE --------
        emoji_count, emoji_list = extract_emojis(emojis)
        emoji_norm = min(emoji_count / 5, 1.0)
        
        # -------- FINAL STRESS SCORE --------
        stress_score = int(
            (visual_score * 0.5 +    # Visual is most important
             text_score * 0.3 +       # Text contributes
             emoji_norm * 0.2) * 100  # Emojis contribute
        )
        
        # Ensure score is between 0-100
        stress_score = max(0, min(100, stress_score))
        
        # Determine stress level and difficulty
        if stress_score >= 70:
            stress_level = "high"
            difficulty = "hard"
            emotion = "Frustration"
        elif stress_score >= 40:
            stress_level = "medium"
            difficulty = "medium"
            emotion = "Anxiety"
        else:
            stress_level = "low"
            difficulty = "easy"
            emotion = "Neutral"
        
        stress_levels[stress_level] += 1
        
        # Detect sarcasm
        sarcastic = is_sarcastic(combined_text, emoji_count)
        if sarcastic:
            emotion = "Sarcasm"
        
        # Insert into database
        cur.execute(insert_query, (
            meme_id, exam, stress_score, stress_level,
            stress_score >= 40, emoji_count, sarcastic,
            emotion, difficulty
        ))
        conn.commit()
        inserted += 1
        
    except Exception as e:
        print(f"❌ Error processing ID {meme_id}: {e}")
        conn.rollback()
        failed_images += 1

# ===============================
# FINAL REPORT
print("\n" + "="*60)
print("📊 FINAL PROCESSING REPORT")
print("="*60)
print(f"✅ Successfully processed: {inserted} memes")
print(f"❌ Failed images: {failed_images}")
print(f"📸 Total attempted: {total_memes}")

print("\n📚 Exam Distribution:")
for exam, count in exam_counter.most_common():
    print(f"  {exam:12}: {count:4} ({count/total_memes*100:.1f}%)")

print("\n📊 Stress Level Distribution:")
cur.execute("""
    SELECT stress_level, COUNT(*) 
    FROM analytics_memes_new 
    GROUP BY stress_level
    ORDER BY 
        CASE stress_level
            WHEN 'low' THEN 1
            WHEN 'medium' THEN 2
            WHEN 'high' THEN 3
        END
""")
for level, count in cur.fetchall():
    pct = count/inserted*100 if inserted > 0 else 0
    bar = "█" * int(pct/5)
    print(f"  {level:8}: {count:4} ({pct:5.1f}%) {bar}")

print("\n🎭 Emotional Labels:")
cur.execute("""
    SELECT emotional_label, COUNT(*) 
    FROM analytics_memes_new 
    GROUP BY emotional_label
    ORDER BY COUNT(*) DESC
""")
for label, count in cur.fetchall():
    pct = count/inserted*100 if inserted > 0 else 0
    print(f"  {label:12}: {count:4} ({pct:5.1f}%)")

print("\n😏 Sarcasm Detection:")
cur.execute("SELECT COUNT(*) FROM analytics_memes_new WHERE is_sarcastic = true")
sarcastic_count = cur.fetchone()[0]
print(f"  Sarcastic memes: {sarcastic_count} ({sarcastic_count/inserted*100:.1f}%)")

print("\n📚 Difficulty Distribution:")
cur.execute("""
    SELECT difficulty_signal, COUNT(*) 
    FROM analytics_memes_new 
    GROUP BY difficulty_signal
    ORDER BY 
        CASE difficulty_signal
            WHEN 'easy' THEN 1
            WHEN 'medium' THEN 2
            WHEN 'hard' THEN 3
        END
""")
for diff, count in cur.fetchall():
    pct = count/inserted*100 if inserted > 0 else 0
    print(f"  {diff:8}: {count:4} ({pct:5.1f}%)")

# Show sample results
print("\n" + "="*60)
print("📝 SAMPLE ANALYZED MEMES")
print("="*60)

cur.execute("""
    SELECT 
        m.id,
        a.exam,
        LEFT(m.final_text, 100) as text,
        a.stress_level,
        a.emotional_label,
        a.is_sarcastic,
        a.difficulty_signal
    FROM memes_raw m
    JOIN analytics_memes_new a ON m.id = a.meme_id
    WHERE a.stress_score IS NOT NULL
    ORDER BY RANDOM()
    LIMIT 5
""")

samples = cur.fetchall()
for i, sample in enumerate(samples, 1):
    print(f"\n{i}. Meme ID: {sample[0]} | Exam: {sample[1]}")
    print(f"   Text: {sample[2][:100]}...")
    print(f"   Analysis: Stress={sample[3]}, Emotion={sample[4]}, Sarcastic={sample[5]}, Difficulty={sample[6]}")

# ===============================
# CLEANUP
conn.commit()
cur.close()
conn.close()

print("\n" + "="*60)
print("✅✅✅ ALL MEMES PROCESSED SUCCESSFULLY!")
print("="*60)
print(f"🎯 Total processed: {inserted} memes")