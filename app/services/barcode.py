# app/services/barcode.py

import boto3
from botocore.exceptions import ClientError
from app.config import AWS_REGION, S3_BUCKET

rek = boto3.client("rekognition", region_name=AWS_REGION)

def scan_barcode_with_rekognition(s3_key: str) -> str | None:
    """
    Call Rekognition.detect_text on the S3 object. Return the first LONG alphanumeric string
    that looks like a barcode (e.g. length > 8). If none, return None.
    """
    try:
        response = rek.detect_text(
            Image={
                "S3Object": {
                    "Bucket": S3_BUCKET,
                    "Name": s3_key
                }
            }
        )
    except ClientError as e:
        print(f"Rekognition error: {e}")
        return None

    for textDetection in response.get("TextDetections", []):
        # Rekognition returns Type="WORD" or "LINE", so pick WORDs that look like barcodes
        if textDetection["Type"] == "WORD":
            candidate = textDetection["DetectedText"]
            # crude heuristic: if it’s all‐caps alphanumeric and length > 8, treat as barcode
            if candidate.isalnum() and len(candidate) >= 8:
                return candidate

    return None