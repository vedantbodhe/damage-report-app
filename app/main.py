# app/main.py

import os
import re
import uuid
import boto3
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import AWS_REGION
from app.services.storage import upload_file_to_s3
from app.services.barcode import scan_barcode_with_rekognition
from app.services.ocr import extract_text_with_textract
from app.services.classify import classify_damage_via_openai
from app.services.mailer import send_damage_report_email

app = FastAPI()

origins = ["http://localhost:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/report-damage/")
async def report_damage(
    image: UploadFile = File(...),
    notify: bool = Form(False),
    senderEmail: str | None = Form(None)
):
    # 1) Save locally
    unique_id = str(uuid.uuid4())
    original_filename = image.filename
    filename = f"{unique_id}_{original_filename}"
    local_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(local_path, "wb") as f:
        f.write(await image.read())

    # 2) Upload to S3
    s3_key = f"{unique_id}/{original_filename}"
    image_url = upload_file_to_s3(local_path, s3_key)

    # 3) Barcode scan via Rekognition
    barcode_value = scan_barcode_with_rekognition(s3_key) or "unknown"

    # 4) Determine recipient_email (senderEmail or OCR)
    recipient_email = None
    if senderEmail:
        recipient_email = senderEmail.strip()
    elif notify:
        ocr_text = extract_text_with_textract(s3_key)
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", ocr_text)
        recipient_email = match.group(0) if match else None

    # 5) Classify damage via OpenAI Vision (pass the S3 URL)
    damage_label = classify_damage_via_openai(image_url)

    # 6) Send email if requested
    email_sent = False
    if notify and recipient_email:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.4;">
            <h1 style="color: #2F4F4F;">Damage Report Notification</h1>
            <p>Dear Sender,</p>
            <p>
              A new damage report has been submitted for one of your packages. 
              Please find the details below:
            </p>
            <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
              <tr>
                <td style="padding: 8px; font-weight: bold; vertical-align: top; width: 150px;">Report ID:</td>
                <td style="padding: 8px;">{unique_id}</td>
              </tr>
              <tr>
                <td style="padding: 8px; font-weight: bold; vertical-align: top;">Timestamp:</td>
                <td style="padding: 8px;">{timestamp}</td>
              </tr>
              <tr>
                <td style="padding: 8px; font-weight: bold; vertical-align: top;">Barcode:</td>
                <td style="padding: 8px;">{barcode_value}</td>
              </tr>
              <tr>
                <td style="padding: 8px; font-weight: bold; vertical-align: top;">Damage Type:</td>
                <td style="padding: 8px; color: #B22222;">{damage_label.capitalize()}</td>
              </tr>
            </table>
            <p>
              <strong>Image Preview:</strong><br/>
              <img src="{image_url}" alt="Package Image" 
                   style="max-width: 400px; border: 1px solid #ddd; margin-top: 10px;" />
            </p>
            <p style="margin-top: 20px;">
              Please review this damage report and let us know if you require any action:
              <ul>
                <li>Return</li>
                <li>Replacement</li>
                <li>Dispose</li>
                <li>Other</li>
              </ul>
            </p>
            <p>
              Thank you,<br/>
              <em>Damage Report App Team</em>
            </p>
          </body>
        </html>
        """

        email_sent = send_damage_report_email(
            to_address=recipient_email,
            subject=f"Damage Report: {damage_label.capitalize()}",
            html_body=html_body
        )

    # 7) Return JSON
    return JSONResponse(
        status_code=200,
        content={
            "reportId": unique_id,
            "barcode": barcode_value,
            "damage": damage_label,
            "emailed": email_sent
        }
    )

@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:
    return JSONResponse({"status": "alive"})