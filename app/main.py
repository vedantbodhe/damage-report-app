# damage-report-app/app/main.py

import os
import re
import uuid
import boto3

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse

from app.config import AWS_REGION
from app.services.storage import upload_file_to_s3
from app.services.barcode import scan_barcode
from app.services.ocr import extract_text_from_image
from app.services.classify import classify_damage_via_openai
from app.services.mailer import send_damage_report_email

# Initialize DynamoDB resource & table
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table("DamageReports")

app = FastAPI()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/report-damage/")
async def report_damage(
    image: UploadFile = File(...),
    notify: bool = Form(False)
):
    """
    1. Save uploaded image locally under UPLOAD_FOLDER.
    2. Upload that image to S3 (returns image_url).
    3. Scan for barcode in the image.
    4. Run OCR to extract text, then regex‐find the first email address.
    5. Classify damage via OpenAI Vision API.
    6. If notify=True and email found, send an HTML email via SES.
    7. Store metadata in DynamoDB (reportId, barcode, damage, imageUrl, email, emailed).
    8. Return JSON with the results.
    """
    # 1. Save the uploaded file locally
    unique_id = str(uuid.uuid4())
    original_filename = image.filename
    filename = f"{unique_id}_{original_filename}"
    local_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(local_path, "wb") as f:
        f.write(await image.read())

    # 2. Upload to S3
    s3_key = f"{unique_id}/{original_filename}"
    image_url = upload_file_to_s3(local_path, s3_key)

    # 3. Scan barcode
    barcode_value = scan_barcode(local_path) or "unknown"

    # 4. OCR → extract first email
    ocr_text = extract_text_from_image(local_path)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", ocr_text)
    recipient_email = email_match.group(0) if email_match else None

    # 5. Classify damage
    damage_label = classify_damage_via_openai(local_path)

    # 6. Send email if requested
    email_sent = False
    if notify and recipient_email:
        subject = f"Damage Report: {damage_label}"
        html_body = (
            f"<h2>Damage: <strong>{damage_label}</strong></h2>"
            f"<p>Barcode (if any): <strong>{barcode_value}</strong></p>"
            f"<p><img src='{image_url}' alt='damage image' /></p>"
        )
        email_sent = send_damage_report_email(
            to_address=recipient_email,
            subject=subject,
            html_body=html_body
        )

    # 7. Store metadata in DynamoDB
    item = {
        "reportId": unique_id,
        "barcode": barcode_value,
        "damage": damage_label,
        "imageUrl": image_url,
        "email": recipient_email or "none",
        "emailed": email_sent
    }
    try:
        table.put_item(Item=item)
    except Exception as e:
        print(f"DynamoDB put_item error: {e}")

    # 8. Return JSON response
    return JSONResponse(
        status_code=200,
        content={
            "reportId": unique_id,
            "barcode": barcode_value,
            "damage": damage_label,
            "emailed": email_sent
        }
    )