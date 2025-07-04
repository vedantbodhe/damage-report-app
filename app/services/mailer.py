# app/services/mailer.py

import boto3
import os
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text     import MIMEText
from email.mime.image    import MIMEImage

AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")
SES_SOURCE = os.getenv("SES_SOURCE", "no-reply@reportmydamage.com")
S3_BUCKET  = os.getenv("S3_BUCKET", "damage-report-app-fulda")

ses_client = boto3.client("ses", region_name=AWS_REGION)
s3_client  = boto3.client("s3", region_name=AWS_REGION)

def send_damage_report_email(
    to_address: str,
    subject: str,
    html_body: str,
    s3_key: str            # <-- now accepted
) -> bool:
    """
    Send an email with an inline image fetched from S3.
    Parameters:
      - to_address: recipient email
      - subject: email subject
      - html_body: HTML content containing <img src="cid:report_image">
      - s3_key:     key of the object in S3 to embed as an inline image
    """
    # Fetch image bytes from S3
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        image_bytes = obj["Body"].read()
    except ClientError as e:
        print(f"[mailer] Failed to download {s3_key} from S3: {e}")
        return False

    # Build the multipart/related message
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"]    = SES_SOURCE
    msg["To"]      = to_address

    # Alternative part (plain + html)
    alt = MIMEMultipart("alternative")
    msg.attach(alt)

    # Plain text fallback
    txt = MIMEText(
        "You have a new damage report. Please view in an HTML-capable client.",
        "plain"
    )
    alt.attach(txt)

    # HTML part
    html = MIMEText(html_body, "html")
    alt.attach(html)

    # Inline image part
    img = MIMEImage(image_bytes)
    img.add_header("Content-ID", "<report_image>")
    img.add_header("Content-Disposition", "inline", filename=os.path.basename(s3_key))
    msg.attach(img)

    # Send via SES
    try:
        ses_client.send_raw_email(
            Source=SES_SOURCE,
            Destinations=[to_address],
            RawMessage={"Data": msg.as_string()},
        )
        return True
    except ClientError as e:
        print(f"[mailer] SES send_raw_email failed: {e}")
        return False