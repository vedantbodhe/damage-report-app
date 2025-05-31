# damage-report-app/app/services/ocr.py

import pytesseract
from PIL import Image

def extract_text_from_image(image_path: str) -> str:
    """
    Opens the image at image_path and runs Tesseract OCR (English + German).
    Returns all detected text as a single string.
    """
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="eng+deu")
    return text