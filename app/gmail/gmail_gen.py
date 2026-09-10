import os
import re
import json
import time
import random
import urllib.request
import urllib.error

API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


def generate_email_with_gemini(command):
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing.")

    prompt = f"""
You are a professional Gmail email writing assistant.

Convert the user's voice command into a professional email.

Rules:
- Do not copy the command literally.
- Do not explain anything.
- Do not invent names, dates, prices, companies, attachments, or facts.
- Keep the email natural and concise.

Output exactly:

Subject: <subject>

BODY:
<email body>

User command:
{command}
"""

    url = (
        f"https://generativelivelanguage.googleapis.com/"
        f"v1beta/models/{MODEL}:generateContent"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000,
        },
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY,
        },
        method="POST",
    )

    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

            # Extract text from response (depends on API shape)
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                # Fallback: stringify whole response
                text = json.dumps(data)

            text = re.sub(r"```(?:text)?|```", "", text).strip()

            subject_match = re.search(r"SUBJECT:\s*(.+)", text, re.I)
            body_match = re.search(r"BODY:\s*([\s\S]+)", text, re.I)

            if not subject_match or not body_match:
                raise RuntimeError("Gemini returned an invalid email format.")

            return {
                "subject": subject_match.group(1).strip(),
                "body": body_match.group(1).strip(),
            }

        except urllib.error.HTTPError as e:
            # If rate limited, retry with exponential backoff
            if getattr(e, "code", None) == 429 and attempt < 3:
                time.sleep((2 ** attempt) + random.random())
                continue
            try:
                details = e.read().decode()
            except Exception:
                details = str(e)
            raise RuntimeError(f"Gemini API error: {details}") from e

        except Exception:
            if attempt == 3:
                raise
            time.sleep((2 ** attempt) + random.random())
            continue
