import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"E:\Program Files\Tesseract-OCR\tesseract.exe"

image_path = r"images/NET/UGC-NET(aug 2024)/page_10.png"  # <-- change this

def ocr_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return pytesseract.image_to_string(gray, lang="eng")

text = ocr_image(image_path)

print("----- OCR OUTPUT START -----")
print(text)
print("----- OCR OUTPUT END -----")
