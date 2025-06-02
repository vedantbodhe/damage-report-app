# app/config.py

from pathlib import Path
from dotenv import load_dotenv
import os

# If a .env file exists at project root, load it
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# AWS region (must match where your AWS resources live)
AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")

# S3 bucket name (exactly as created in S3 Console)
S3_BUCKET = os.getenv("S3_BUCKET", "damage-report-app-fulda")

# SES verified "From" email address
SES_SOURCE = os.getenv("SES_SOURCE", "vedantbodhe@gmail.com")

# OpenAI API key (for Vision API)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")