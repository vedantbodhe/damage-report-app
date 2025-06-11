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

# Serve static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Uploads dir
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
    # Log incoming parameters
    logger.info(f"[REPORT] notify={notify}, senderEmail={senderEmail!r}")

    # 1. Save locally
    report_id = str(uuid.uuid4())
    filename = f"{report_id}_{image.filename}"
    local_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(local_path, "wb") as f:
        f.write(await image.read())
    logger.info(f"[REPORT] Saved file to {local_path}")

    # 2. Upload to S3
    s3_key = f"{report_id}/{image.filename}"
    image_url = upload_file_to_s3(local_path, s3_key)
    logger.info(f"[REPORT] Uploaded to S3 at key {s3_key}")

    # 3. Barcode scan
    try:
        barcode = scan_barcode_with_rekognition(s3_key) or "unknown"
    except Exception as e:
        logger.error(f"[REPORT] Barcode scan failed: {e}")
        barcode = "error"
    logger.info(f"[REPORT] Barcode value: {barcode}")

    # 4. Classify damage
    try:
        damage = classify_damage_via_openai(image_url)
    except Exception as e:
        logger.error(f"[REPORT] Damage classification failed: {e}")
        damage = "error"
    logger.info(f"[REPORT] Damage label: {damage}")

    # 5. Send email only if requested AND we have a senderEmail
    emailed = False
    if notify:
        if senderEmail:
            logger.info(f"[REPORT] Sending email to {senderEmail}")
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            html_body = f"""
            <html>
              <body style="font-family:Arial,sans-serif;line-height:1.4">
                <h1>Damage Report Notification</h1>
                <ul>
                  <li><strong>Report ID:</strong> {report_id}</li>
                  <li><strong>Timestamp:</strong> {timestamp}</li>
                  <li><strong>Barcode:</strong> {barcode}</li>
                  <li><strong>Damage:</strong> {damage.capitalize()}</li>
                </ul>
                <p>
                  <img src="{image_url}" 
                       style="max-width:400px;border:1px solid #ddd"
                       alt="Damage Image"/>
                </p>
              </body>
            </html>
            """
            try:
                emailed = send_damage_report_email(
                    to_address=senderEmail,
                    subject=f"Damage Report: {damage.capitalize()}",
                    html_body=html_body,
                    s3_key=s3_key,
                )
                logger.info(f"[REPORT] Email sent: {emailed}")
            except Exception as e:
                logger.error(f"[REPORT] Email send failed: {e}")
                emailed = False
        else:
            logger.warning("[REPORT] notify=True but no senderEmail provided; skipping email")
    else:
        logger.info("[REPORT] notify=False, skipping email")

    # 6. Return JSON
    return JSONResponse(
        {
            "reportId": report_id,
            "barcode": barcode,
            "damage": damage,
            "emailed": emailed,
        }
    )


@app.get("/health", include_in_schema=False)
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "alive"})