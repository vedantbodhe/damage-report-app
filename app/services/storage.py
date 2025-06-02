# app/services/storage.py

import boto3
import os
from urllib.parse import quote_plus

from app.config import AWS_REGION, S3_BUCKET

s3 = boto3.client("s3", region_name=AWS_REGION)

def upload_file_to_s3(local_path: str, s3_key: str) -> str:
    """
    Upload the local file at `local_path` into S3 under the key `s3_key`.
    Returns the public URL to that object (assuming the bucket allows public‐read).
    """
    content_type = None
    # Optionally infer ContentType from the filename extension:
    ext = os.path.splitext(local_path)[1].lower()
    if ext in {".jpg", ".jpeg"}:
        content_type = "image/jpeg"
    elif ext == ".png":
        content_type = "image/png"
    # etc...

    s3.upload_file(
        Filename=local_path,
        Bucket=S3_BUCKET,
        Key=s3_key,

    )

    # Construct a URL‐encoded public URL:
    return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{quote_plus(s3_key)}"