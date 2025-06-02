# damage-report-app/app/services/barcode.py

from PIL import Image
from pyzbar.pyzbar import decode

def scan_barcode(image_path: str) -> str | None:
    """
    Opens the image at image_path and attempts to decode any barcodes (1D or QR).
    Returns the first decoded string (UTF-8) if found, otherwise None.
    """
    img = Image.open(image_path)
    decoded_objects = decode(img)
    if decoded_objects:
        return decoded_objects[0].data.decode("utf-8")
    return None