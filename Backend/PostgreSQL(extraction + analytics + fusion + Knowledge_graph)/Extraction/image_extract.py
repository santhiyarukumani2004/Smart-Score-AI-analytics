import os
from pdf2image import convert_from_path

# -----------------------------
# CONFIG
# -----------------------------
PDF_ROOT = "pdfs"          # pdfs/GATE/gate-2023(fn).pdf
IMAGE_ROOT = "images/NET"      # images/GATE/gate-2023(fn)/
POPPLER_PATH = r"E:\poppler\poppler-23.11.0\Library\bin"

os.makedirs(IMAGE_ROOT, exist_ok=True)

# -----------------------------
# PDF → IMAGE FUNCTION
# -----------------------------
def pdf_to_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    pages = convert_from_path(
        pdf_path,
        dpi=300,
        poppler_path=POPPLER_PATH
    )

    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder, f"page_{i+1}.png")
        page.save(image_path, "PNG")

    print(f"✅ Converted: {pdf_path} → {len(pages)} images")

# -----------------------------
# MAIN LOOP
# -----------------------------
for pdf_file in os.listdir(PDF_ROOT):
    if pdf_file.lower().endswith(".pdf"):
        pdf_path = os.path.join(PDF_ROOT, pdf_file)

        folder_name = pdf_file.replace(".pdf", "")
        output_folder = os.path.join(IMAGE_ROOT, folder_name)

        pdf_to_images(pdf_path, output_folder)


