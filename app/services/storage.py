# damage-report-app/app/services/storage.py

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from ..config import AWS_REGION, S3_BUCKET

# Initialize S3 client
s3_client = boto3.client("s3", region_name=AWS_REGION)

def upload_file_to_s3(local_path: str, s3_key: str) -> str:
    """
    Uploads the file at local_path to the S3 bucket under the given s3_key.
    Returns the HTTPS URL of the uploaded object.
    Raises RuntimeError if upload fails.
    """
    try:
        s3_client.upload_file(local_path, S3_BUCKET, s3_key)
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 upload failed: {e}")

    return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"