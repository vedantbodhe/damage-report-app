# damage-report-app/tests/test_barcode.py

from app.services.barcode import scan_barcode
from PIL import Image
from pathlib import Path
import pytest

def test_scan_barcode_with_no_code(tmp_path):
    # Create a blank white image
    img_path = tmp_path / "blank.jpg"
    Image.new("RGB", (200, 200), color="white").save(str(img_path))

    result = scan_barcode(str(img_path))
    assert result is None

def test_scan_barcode_with_sample_qr():
    # Assumes you have placed a valid QR code image at tests/sample_qr.png
    sample_qr_path = Path("tests/sample_qr.png")
    if not sample_qr_path.exists():
        pytest.skip("No sample_qr.png found for barcode test")
    result = scan_barcode(str(sample_qr_path))
    # If that QR code encodes "HELLO", this should match
    assert result == "HELLO"