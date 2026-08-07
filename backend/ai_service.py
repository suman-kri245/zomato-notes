import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=GEMINI_API_KEY)

print("Gemini API key loaded successfully")


def get_ai_response(title, content):
    prompt = (
        "Generate one short lowercase tag for this note.\n"
        f"Title: {title}\n"
        f"Content: {content}\n"
        "Return only the tag."
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        tag = response.text.strip().lower()
        tag = tag.replace("#", "").strip()

        if not tag:
            return "general"

        print("AI Generated Tag:", tag)
        return tag

    except Exception as e:
        print("AI Error:", e)
        return "general"