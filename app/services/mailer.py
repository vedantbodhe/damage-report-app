# app/services/mailer.py

import boto3
from botocore.exceptions import ClientError
from app.config import AWS_REGION, SES_SOURCE

_ses_client = boto3.client("ses", region_name=AWS_REGION)

def send_damage_report_email(to_address: str, subject: str, html_body: str) -> bool:
    print(f"DEBUG ▶ send_damage_report_email called with to_address={to_address}")

    if not SES_SOURCE:
        print("MAILER: SES_SOURCE is not configured; skipping email.")
        return False

    try:
        resp = _ses_client.send_email(
            Source=SES_SOURCE,
            Destination={"ToAddresses": [to_address]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": html_body}}
            }
        )
        print("MAILER: SES send_email succeeded, MessageId:", resp["MessageId"])
        return True
    except ClientError as e:
        print("MAILER: SES send_email failed:", e.response["Error"]["Message"])
        return False
    finally:
        print("DEBUG ▶ send_damage_report_email finished")