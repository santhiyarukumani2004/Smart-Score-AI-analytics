import os
from pdf2image import convert_from_path

PDF_DIR = "pdfs"
IMAGE_DIR = "images"

os.makedirs(IMAGE_DIR, exist_ok=True)

for pdf_file in os.listdir(PDF_DIR):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]

        output_folder = os.path.join(IMAGE_DIR, pdf_name)
        os.makedirs(output_folder, exist_ok=True)

        images = convert_from_path(pdf_path, dpi=300)

        for i, img in enumerate(images):
            img.save(f"{output_folder}/page_{i+1}.png", "PNG")

        print(f"✅ Converted: {pdf_file} → {len(images)} pages")
