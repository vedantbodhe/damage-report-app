# damage-report-app/tests/test_ocr.py

from app.services.ocr import extract_text_from_image
from PIL import Image, ImageDraw
import pytest

def test_ocr_blank_image(tmp_path):
    img_path = tmp_path / "blank.jpg"
    Image.new("RGB", (200, 200), color="white").save(str(img_path))

    text = extract_text_from_image(str(img_path))
    assert text.strip() == ""

def test_ocr_simple_email(tmp_path):
    # Draw "test@example.com" on a white image
    img = Image.new("RGB", (400, 100), color="white")
    d = ImageDraw.Draw(img)
    d.text((10, 10), "test@example.com", fill=(0, 0, 0))
    img_path = tmp_path / "email.jpg"
    img.save(str(img_path))

    text = extract_text_from_image(str(img_path))
    assert "test@example.com" in text.lower()