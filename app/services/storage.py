# app/services/storage.py

import os
import mimetypes
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import AWS_REGION, S3_BUCKET

_s3_client = boto3.client("s3", region_name=AWS_REGION)

def upload_file_to_s3(local_path: str, s3_key: str) -> str:
    """
    Uploads the file at local_path to S3 under key s3_key,
    and returns the public URL. Does NOT set an object ACL.
    Assumes your bucket policy already allows public-read.
    """
    content_type = _guess_content_type(local_path)

    try:
        _s3_client.upload_file(
            Filename=local_path,
            Bucket=S3_BUCKET,
            Key=s3_key,
            ExtraArgs={"ContentType": content_type}
        )
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 upload failed: {e}")

    region = AWS_REGION
    return f"https://{S3_BUCKET}.s3.{region}.amazonaws.com/{s3_key}"

def _guess_content_type(file_path: str) -> str:
    mtype, _ = mimetypes.guess_type(file_path)
    return mtype or "application/octet-stream"