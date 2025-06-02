# app/services/barcode.py

import boto3
from botocore.exceptions import ClientError
from app.config import AWS_REGION, S3_BUCKET

rek = boto3.client("rekognition", region_name=AWS_REGION)

def scan_barcode_with_rekognition(s3_key: str) -> str | None:
    """
    Rekognition has been disabled for now.
    Always return None so main.py will fall back to "unknown".
    """
    return None