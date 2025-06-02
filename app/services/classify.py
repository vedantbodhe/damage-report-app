# app/services/classify.py

from openai import OpenAI

# Initialize OpenAI client (will pick up OPENAI_API_KEY from environment)
client = OpenAI()

# Valid damage labels
VALID_LABELS = {"scratch", "tear", "break", "dent", "other"}

def classify_damage_via_openai(image_url: str) -> str:
    """
    Given a publicly accessible image_url (e.g. from S3), call OpenAI Vision via:
      client.responses.create(
        model="gpt-4.1-mini",
        input=[{
          "role": "user",
          "content": [
            { "type": "input_text",  "text": <prompt> },
            { "type": "input_image", "image_url": <image_url> }
          ]
        }]
      )
    Then parse response.output_text for one of VALID_LABELS.
    """
    prompt_text = (
        "Classify the damage in this package image. "
        "Reply with one of these or if other, then explain in two words what it is: scratch, tear, break, dent, or other."
    )

    message = {
        "role": "user",
        "content": [
            {"type": "input_text",  "text": prompt_text},
            {"type": "input_image", "image_url": image_url}
        ],
    }

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",   # or "gpt-4o-mini" if available
            input=[message]
        )
    except Exception as e:
        raise RuntimeError(f"OpenAI Vision response failed: {e}")

    output = response.output_text.strip().lower()
    return output if output in VALID_LABELS else "other"