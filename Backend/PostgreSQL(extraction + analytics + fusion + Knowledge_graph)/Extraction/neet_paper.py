import os
from pdf2image import convert_from_path

PDF_DIR = "pdfs"
IMAGE_DIR = "images/JEE"

os.makedirs(IMAGE_DIR, exist_ok=True)

for pdf_file in os.listdir(PDF_DIR):
    if pdf_file.lower().endswith(".pdf"):
        
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]
        
        output_dir = os.path.join(IMAGE_DIR, pdf_name)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Processing {pdf_file} ...")
        
        images = convert_from_path(pdf_path, dpi=300)
        
        for i, img in enumerate(images):
            img.save(os.path.join(output_dir, f"page_{i+1}.png"), "PNG")
        
        print(f"Saved {len(images)} pages for {pdf_file}\n")

print("ALL PDFs converted to images successfully!")
