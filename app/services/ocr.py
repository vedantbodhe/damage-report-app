# app/services/ocr.py

import boto3
from botocore.exceptions import ClientError
from app.config import AWS_REGION, S3_BUCKET

textract = boto3.client("textract", region_name=AWS_REGION)

def extract_text_with_textract(s3_key: str) -> str:
    """
    Pull raw text from an image in S3 via AWS Textract.
    Returns the concatenated plain text (all pages).
    """
    try:
        response = textract.detect_document_text(
            Document={
                "S3Object": {
                    "Bucket": S3_BUCKET,
                    "Name": s3_key
                }
            }
        )
    except ClientError as e:
        print(f"Textract error: {e}")
        return ""

    lines = []
    for block in response.get("Blocks", []):
        if block["BlockType"] == "LINE":
            lines.append(block["Text"])
    return "\n".join(lines)