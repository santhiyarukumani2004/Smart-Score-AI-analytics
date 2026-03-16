import os
import re
import cv2
import pytesseract
import pandas as pd
from collections import Counter

# Updated paths for NET
IMAGE_ROOT = "images/NET"
OUTPUT_CSV = "output/NET_CS_questions1.csv"
OUTPUT_SUMMARY_CSV = "output/net_question_summary.csv"

pytesseract.pytesseract.tesseract_cmd = r"E:\Program Files\Tesseract-OCR\tesseract.exe"

os.makedirs("output", exist_ok=True)

def parse_net_folder(folder_name):
    """Extracts year, month from folder name"""
    folder_name = folder_name.lower()
    
    year_match = re.search(r"(20\d{2})", folder_name)
    year = year_match.group(1) if year_match else "Unknown"
    
    month_keywords = {
        'jan': 'January', 'feb': 'February', 'mar': 'March',
        'apr': 'April', 'may': 'May', 'jun': 'June',
        'jul': 'July', 'aug': 'August', 'sep': 'September',
        'oct': 'October', 'nov': 'November', 'dec': 'December'
    }
    
    month = "Unknown"
    for key, value in month_keywords.items():
        if key in folder_name:
            month = value
            break
    
    return year, month, "Paper 2", "2", "Computer Science and Applications"

def ocr_image(image_path):
    """Optimized OCR for NET papers"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return ""
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply multiple preprocessing steps
        # 1. Denoise
        gray = cv2.medianBlur(gray, 3)
        
        # 2. Threshold
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # 3. OCR with multiple PSM modes
        configs = [
            '--psm 6 --oem 3 -l eng',   # Uniform block
            '--psm 4 --oem 3 -l eng',   # Single column
            '--psm 11 --oem 3 -l eng',  # Sparse text
            '--psm 3 --oem 3 -l eng',   # Automatic
        ]
        
        best_text = ""
        max_length = 0
        
        for config in configs:
            try:
                text = pytesseract.image_to_string(thresh, config=config)
                if len(text) > max_length:
                    max_length = len(text)
                    best_text = text
            except:
                continue
        
        return best_text
    except Exception as e:
        print(f"  OCR Error: {str(e)}")
        return ""

# -----------------------------
# EXTREMELY ROBUST QUESTION DETECTION
# -----------------------------
def extract_questions_from_net_text(text):
    """
    Multiple pattern matching strategies for NET questions
    """
    if not text or len(text.strip()) < 50:
        return []
    
    questions = []
    
    # STRATEGY 1: Look for "SubQuestion No:" pattern (your actual format)
    patterns = [
        # Pattern 1: "SubQuestion No: 5" (your format)
        r'SubQuestion\s*No\.?\s*:?\s*(\d+)',
        
        # Pattern 2: "SubQuestion No 5" (without colon)
        r'SubQuestion\s*No\.?\s*(\d+)',
        
        # Pattern 3: "SubQuestion : 5" 
        r'SubQuestion\s*:?\s*(\d+)',
        
        # Pattern 4: Just "Q.5" or "Q5"
        r'Q\.?\s*(\d+)',
    ]
    
    # Try each pattern
    for pattern in patterns:
        # Split the text by the pattern
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        
        if len(parts) > 1:
            # We found matches with this pattern
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    question_number = parts[i].strip()
                    question_content = parts[i + 1].strip()
                    
                    # Extract question text
                    question_text = extract_question_text_robust(question_content)
                    
                    if question_text and len(question_text.split()) > 3:
                        questions.append({
                            'number': question_number,
                            'text': question_text,
                            'full_content': question_content[:500]  # Store first 500 chars
                        })
            
            if questions:
                break  # Stop if we found questions with this pattern
    
    # STRATEGY 2: If no questions found, look for numbered items
    if not questions:
        lines = text.split('\n')
        current_q_num = None
        current_q_text = []
        
        for line in lines:
            line = line.strip()
            
            # Check for question number patterns
            q_match = re.match(r'^(\d+)\.\s+(.+)', line)
            if not q_match:
                q_match = re.match(r'^Q\.?\s*(\d+)[\.\s]+(.+)', line, re.IGNORECASE)
            
            if q_match:
                # Save previous question
                if current_q_num and current_q_text:
                    q_text = ' '.join(current_q_text).strip()
                    questions.append({
                        'number': current_q_num,
                        'text': q_text,
                        'full_content': q_text
                    })
                
                # Start new question
                current_q_num = q_match.group(1)
                current_q_text = [q_match.group(2)]
            elif current_q_num and line and not line.startswith('http'):
                current_q_text.append(line)
        
        # Add last question
        if current_q_num and current_q_text:
            q_text = ' '.join(current_q_text).strip()
            questions.append({
                'number': current_q_num,
                'text': q_text,
                'full_content': q_text
            })
    
    # STRATEGY 3: Look for the exact format from your sample
    if not questions:
        # Look for patterns like: "Q.5 If the number of males..."
        matches = re.finditer(r'Q\.?\s*(\d+)\s+([^Q]+?)(?=Q\.|\Z)', text, re.DOTALL | re.IGNORECASE)
        for match in matches:
            q_num = match.group(1)
            q_text = match.group(2).strip()
            # Clean the text
            q_text = re.sub(r'Question Type.*$', '', q_text, flags=re.DOTALL | re.IGNORECASE)
            q_text = re.sub(r'Options.*$', '', q_text, flags=re.DOTALL | re.IGNORECASE)
            q_text = q_text.strip()
            
            if q_text and len(q_text.split()) > 3:
                questions.append({
                    'number': q_num,
                    'text': q_text,
                    'full_content': q_text
                })
    
    return questions

def extract_question_text_robust(content):
    """Extract question text using multiple strategies"""
    
    # Strategy 1: Look for the question before "Options" or "Question Type"
    text = content
    
    # Cut off at common markers
    markers = [
        'Question Type :',
        'Question ID :',
        'Options',
        'Option 1 ID :',
        'Status :',
        'Chosen Option :',
        'http',
        'https://'
    ]
    
    for marker in markers:
        if marker in text:
            text = text.split(marker)[0]
    
    # Strategy 2: Remove lines with URLs
    lines = text.split('\n')
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('http') and not line.startswith('https'):
            # Skip lines that are just numbers or metadata
            if re.match(r'^\d+\s*$', line):
                continue
            if re.match(r'^[A-Za-z]+\s*\d+\s*$', line):  # Like "Page 5"
                continue
            clean_lines.append(line)
    
    # Join and clean
    question_text = ' '.join(clean_lines)
    
    # Remove common prefixes
    question_text = re.sub(r'^Q\.?\s*\d+\s*', '', question_text)
    question_text = re.sub(r'^\d+\.\s*', '', question_text)
    question_text = re.sub(r'^SubQuestion\s*No\.?\s*:?\s*\d+\s*', '', question_text, flags=re.IGNORECASE)
    
    return question_text.strip()

def classify_question_topic(q):
    """Classify the question topic"""
    q_lower = q.lower()
    
    # Data Interpretation questions (like your example)
    if any(term in q_lower for term in ['arts', 'science', 'commerce', 'students', 'passed', 'city', 'proportion']):
        return "Data Interpretation"
    
    # Computer Science topics
    cs_topics = {
        "Programming": ['program', 'code', 'function', 'array', 'pointer', 'class', 'object'],
        "Algorithms": ['algorithm', 'sort', 'search', 'complexity', 'dynamic programming'],
        "Data Structures": ['linked list', 'stack', 'queue', 'tree', 'graph', 'binary'],
        "Databases": ['sql', 'query', 'database', 'table', 'normalization'],
        "Networks": ['network', 'protocol', 'ip', 'tcp', 'http'],
        "Operating Systems": ['process', 'thread', 'memory', 'scheduling', 'deadlock'],
    }
    
    for topic, keywords in cs_topics.items():
        for keyword in keywords:
            if keyword in q_lower:
                return topic
    
    return "General"

# -----------------------------
# DEBUG FUNCTION TO SEE RAW OCR
# -----------------------------
def debug_ocr_output(image_path):
    """Debug function to see exactly what OCR is returning"""
    print(f"\n🔍 DEBUG MODE: {image_path}")
    print("-" * 50)
    
    text = ocr_image(image_path)
    
    print("📝 RAW OCR TEXT (first 1000 chars):")
    print("-" * 50)
    print(text[:1000])
    print("-" * 50)
    
    print("\n🔎 SEARCHING FOR QUESTION PATTERNS...")
    
    # Check for various patterns
    patterns_to_check = [
        ('SubQuestion No:', 'SubQuestion\\s*No\\.?\\s*:?'),
        ('SubQuestion', 'SubQuestion'),
        ('Q.', 'Q\\.'),
        ('Q5', 'Q\\s*5'),
        ('5.', '5\\.'),
    ]
    
    for name, pattern in patterns_to_check:
        matches = re.findall(pattern, text, re.IGNORECASE)
        print(f"  {name}: {'✅ Found' if matches else '❌ Not found'} - {matches[:5]}")
    
    questions = extract_questions_from_net_text(text)
    print(f"\n📊 Questions extracted: {len(questions)}")
    
    for i, q in enumerate(questions[:2]):
        print(f"\n  Question {i+1}:")
        print(f"    Number: {q['number']}")
        print(f"    Text: {q['text'][:100]}...")
    
    return questions

# -----------------------------
# MAIN PROCESSING FUNCTION
# -----------------------------
def process_net_papers():
    """Main function to process NET papers"""
    rows = []
    stats = {
        'total_images': 0,
        'images_with_questions': 0,
        'total_questions': 0,
        'failed_images': 0
    }
    
    print("="*60)
    print("UGC NET QUESTION PAPER PROCESSOR")
    print("="*60)
    
    if not os.path.exists(IMAGE_ROOT):
        print(f"Error: Directory not found: {IMAGE_ROOT}")
        return None
    
    folders = [f for f in os.listdir(IMAGE_ROOT) if os.path.isdir(os.path.join(IMAGE_ROOT, f))]
    print(f"Found {len(folders)} folders")
    
    for folder_idx, year_folder in enumerate(sorted(folders), 1):
        folder_path = os.path.join(IMAGE_ROOT, year_folder)
        year, month, paper, paper_code, subject = parse_net_folder(year_folder)
        
        print(f"\n[{folder_idx}/{len(folders)}] 📁 {year_folder}")
        
        # Get images
        image_extensions = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp')
        image_files = [f for f in sorted(os.listdir(folder_path)) 
                      if f.lower().endswith(image_extensions)]
        
        if not image_files:
            continue
        
        print(f"  Found {len(image_files)} images")
        
        for img_idx, img_file in enumerate(image_files, 1):
            image_path = os.path.join(folder_path, img_file)
            stats['total_images'] += 1
            
            print(f"    [{img_idx}/{len(image_files)}] {img_file}", end="")
            
            # OCR
            text = ocr_image(image_path)
            
            if not text or len(text.strip()) < 50:
                print(" - ⚠️ No text")
                stats['failed_images'] += 1
                continue
            
            # Extract questions
            questions = extract_questions_from_net_text(text)
            
            if not questions:
                print(" - ❌ No questions")
                continue
            
            print(f" - ✅ {len(questions)} questions")
            stats['images_with_questions'] += 1
            stats['total_questions'] += len(questions)
            
            # Process each question
            for q in questions:
                topic = classify_question_topic(q['text'])
                
                rows.append({
                    "exam": "UGC NET",
                    "year": year,
                    "month": month,
                    "paper": paper,
                    "paper_code": paper_code,
                    "subject": subject,
                    "topic": topic,
                    "question_number": q['number'],
                    "question_text": q['text'],
                    "question_length": len(q['text'].split()),
                    "difficulty": "Medium",  # Default
                    "bloom_level": "Apply",  # Default
                    "source_folder": year_folder,
                    "source_image": img_file,
                })
    
    # Create DataFrame
    if not rows:
        print("\n❌ No questions found in any image!")
        return None
    
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    # Print summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Images processed: {stats['total_images']}")
    print(f"Images with questions: {stats['images_with_questions']}")
    print(f"Total questions: {stats['total_questions']}")
    print(f"Failed images: {stats['failed_images']}")
    print(f"\n✅ Saved to: {OUTPUT_CSV}")
    
    return df

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        # Debug mode
        test_image = r"images/NET/UGC-NET(aug 2024)/page_5.png"
        if os.path.exists(test_image):
            debug_ocr_output(test_image)
        else:
            print(f"Test image not found: {test_image}")
            # Find any image to test
            for root, dirs, files in os.walk("images/NET"):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg')):
                        test_image = os.path.join(root, file)
                        debug_ocr_output(test_image)
                        break
                break
    else:
        # Normal processing
        df = process_net_papers()