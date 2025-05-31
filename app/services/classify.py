# damage-report-app/app/services/classify.py

import openai
from ..config import OPENAI_API_KEY

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

PROMPT = (
    "You are an assistant specialized in parcel damage classification.\n"
    "Classify the visible damage into exactly one of these labels (lowercase): "
    "scratch, tear, break, dent, or other.\n"
    "Reply with only the label (no extra text)."
)

def classify_damage_via_openai(image_path: str) -> str:
    """
    Sends the image to OpenAI Vision API (LABEL_DETECTION).
    Returns the most confident label in lowercase.
    If no labels found, returns 'other'.
    """
    try:
        with open(image_path, "rb") as img_file:
            response = openai.Vision.analyze(
                image=img_file,
                features=["LABEL_DETECTION"]
            )
    except Exception as e:
        raise RuntimeError(f"OpenAI Vision API call failed: {e}")

    labels = response.get("labels", [])
    if labels:
        return labels[0]["description"].lower()
    return "other"