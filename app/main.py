# app/main.py

import os
import uuid
from datetime import datetime
import logging

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import AWS_REGION
from app.services.storage import upload_file_to_s3
from app.services.classify import classify_damage_via_openai
from app.services.mailer import send_damage_report_email
from app.services.barcode import scan_barcode_with_rekognition

# Set up logger
logger = logging.getLogger("uvicorn.error")

app = FastAPI()

# ───── CORS ────────────────────────────────────────────────────────────────
origins = [
    "http://localhost:8000",
    "http://localhost:8080",
    "https://reportmydamage.com",
    "http://reportmydamage.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ────────────────────────────────────────────────────────────────────────────

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure uploads folder exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/", include_in_schema=False)
async def serve_menu() -> HTMLResponse:
    path = os.path.join("static", "menu.html")
    if not os.path.isfile(path):
        return HTMLResponse("<h1>Menu not found</h1>", status_code=404)
    return HTMLResponse(open(path, encoding="utf-8").read(), status_code=200)


@app.get("/form", include_in_schema=False)
async def serve_form() -> HTMLResponse:
    path = os.path.join("static", "frontend.html")
    if not os.path.isfile(path):
        return HTMLResponse("<h1>Form not found</h1>", status_code=404)
    return HTMLResponse(open(path, encoding="utf-8").read(), status_code=200)


@app.post("/report-damage/")
async def report_damage(
    image: UploadFile = File(...),
    notify: bool = Form(False),
    senderEmail: str | None = Form(None),
):
    # Log inputs
    logger.info(f"[REPORT] notify={notify}, senderEmail={senderEmail!r}")

    # 1) Save locally
    report_id = str(uuid.uuid4())
    filename = f"{report_id}_{image.filename}"
    local_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(local_path, "wb") as f:
        f.write(await image.read())
    logger.info(f"[REPORT] Saved file to {local_path}")

    # 2) Upload to S3
    s3_key = f"{report_id}/{image.filename}"
    image_url = upload_file_to_s3(local_path, s3_key)
    logger.info(f"[REPORT] Uploaded to S3 at key {s3_key}")

    # 3) Barcode scan
    try:
        barcode = scan_barcode_with_rekognition(s3_key) or "unknown"
    except Exception as e:
        logger.error(f"[REPORT] Barcode scan failed: {e}")
        barcode = "unknown"
    logger.info(f"[REPORT] Barcode value: {barcode}")

    # 4) Classify damage
    try:
        damage = classify_damage_via_openai(image_url)
    except Exception as e:
        logger.error(f"[REPORT] Damage classification failed: {e}")
        damage = "unknown"
    logger.info(f"[REPORT] Damage label: {damage}")

    # 5) Send email if requested
    emailed = False
    if notify and senderEmail:
        logger.info(f"[REPORT] Sending email to {senderEmail}")
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; margin:0; padding:0; background:#f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td align="center" style="padding:20px 0;">
                  <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                      <td style="background:#2563eb; padding:20px; text-align:center;">
                        <h1 style="color:#ffffff; font-size:24px; margin:0;">Damage Report Notification</h1>
                      </td>
                    </tr>
                    <!-- Body -->
                    <tr>
                      <td style="padding:20px; color:#333333; font-size:16px;">
                        <p style="margin:0 0 16px;">Dear Sender,</p>
                        <p style="margin:0 0 16px;">
                          A new damage report has been filed. Please review the details below:
                        </p>
                        <table width="100%" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
                          <tr>
                            <td style="font-weight:bold; width:150px; border-bottom:1px solid #eeeeee;">Report ID:</td>
                            <td style="border-bottom:1px solid #eeeeee;">{report_id}</td>
                          </tr>
                          <tr>
                            <td style="font-weight:bold; border-bottom:1px solid #eeeeee;">Timestamp:</td>
                            <td style="border-bottom:1px solid #eeeeee;">{timestamp}</td>
                          </tr>
                          <tr>
                            <td style="font-weight:bold; border-bottom:1px solid #eeeeee;">Barcode:</td>
                            <td style="border-bottom:1px solid #eeeeee;">{barcode}</td>
                          </tr>
                          <tr>
                            <td style="font-weight:bold; border-bottom:1px solid #eeeeee;">Damage:</td>
                            <td style="border-bottom:1px solid #eeeeee; color:#b22222;">{damage.capitalize()}</td>
                          </tr>
                        </table>
                        <p style="margin:20px 0; text-align:center;">
                          <img src="cid:report_image" alt="Damage Image"
                               style="max-width:100%; border:1px solid #cccccc; border-radius:4px;"/>
                        </p>
                        <p style="margin:0 0 16px;">
                          If you require further action (return, replacement, disposal), please respond to this email.
                        </p>
                        <p style="margin:0;">Thank you,<br/><em>Report My Damage! Team</em></p>
                      </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                      <td style="background:#f0f0f0; padding:10px; text-align:center; font-size:12px; color:#888888;">
                        © 2025 Report My Damage! | <a href="https://reportmydamage.com" style="color:#2563eb; text-decoration:none;">Visit our site</a>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """
        try:
            emailed = send_damage_report_email(
                to_address=senderEmail,
                subject=f"Damage Report: {damage.capitalize()}",
                html_body=html_body,
                s3_key=s3_key,  # pass the key so mailer can fetch inline
            )
            logger.info(f"[REPORT] Email sent: {emailed}")
        except Exception as e:
            logger.error(f"[REPORT] Email send failed: {e}")
            emailed = False
    else:
        logger.info("[REPORT] Not sending email (either notify=False or no senderEmail)")

    # 6) Return JSON
    return JSONResponse({
        "reportId": report_id,
        "barcode": barcode,
        "damage": damage,
        "emailed": emailed
    })


@app.get("/health", include_in_schema=False)
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "alive"})