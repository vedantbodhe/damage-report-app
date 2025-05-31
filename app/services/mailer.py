# damage-report-app/app/services/mailer.py

import boto3
from botocore.exceptions import ClientError
from ..config import AWS_REGION, SES_SOURCE

# Initialize SES client
ses_client = boto3.client("ses", region_name=AWS_REGION)

def send_damage_report_email(
    to_address: str,
    subject: str,
    html_body: str
) -> bool:
    """
    Sends an HTML email via AWS SES.
    Returns True if sent successfully; False otherwise.
    """
    try:
        ses_client.send_email(
            Source=SES_SOURCE,
            Destination={"ToAddresses": [to_address]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": html_body}},
            }
        )
        return True
    except ClientError as e:
        print(f"SES send_email error: {e.response['Error']['Message']}")
        return False