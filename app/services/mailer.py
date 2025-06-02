# app/services/mailer.py

import boto3
from botocore.exceptions import ClientError
from app.config import AWS_REGION, SES_SOURCE

ses = boto3.client("ses", region_name=AWS_REGION)

def send_damage_report_email(
    to_address: str,
    subject: str,
    html_body: str
) -> bool:
    """
    Sends an HTML email via AWS SES. Returns True on success, False on failure.
    """
    try:
        ses.send_email(
            Source=SES_SOURCE,
            Destination={"ToAddresses": [to_address]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": html_body}},
            },
        )
        return True
    except ClientError:
        return False