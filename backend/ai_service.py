import os
import json
import re

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# AI PROMPT TEMPLATE
# ============================================================

AI_PROMPT_TEMPLATE = """
Instructions:
Read the provided note and generate useful tags and a short summary.

Context:
The note belongs to an internal engineering knowledge-base application.

Input:
Note content:
{content}

Constraints:
- Return only a valid JSON object.
- The JSON object must contain exactly two keys: "tags" and "summary".
- "tags" must be a list containing 1 to 3 short lowercase keyword strings.
- "summary" must be one sentence containing at most 20 words.
- No text may surround the JSON object.
- Do not use markdown code fences.

Output Format:
{
  "tags": ["keyword1", "keyword2"],
  "summary": "Short summary of the note."
}
"""


# ============================================================
# MOCK AI
# ============================================================

def mock_ai_response(user_message: str) -> str:
    """
    Deterministic offline AI response.
    No API key and no network connection are required.
    """

    text = user_message.strip()

    if not text:
        return json.dumps(
            {
                "tags": ["general"],
                "summary": "Empty note content."
            }
        )

    words = re.findall(r"[A-Za-z0-9]+", text.lower())

    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "was",
        "were",
        "and",
        "or",
        "to",
        "of",
        "in",
        "on",
        "for",
        "with",
        "this",
        "that",
        "because",
        "after",
        "before",
        "from",
        "by",
        "as",
        "it",
    }

    significant_words = []

    for word in words:
        if word not in stop_words and word not in significant_words:
            significant_words.append(word)

        if len(significant_words) == 3:
            break

    if not significant_words:
        significant_words = ["general"]

    first_sentence = re.split(r"[.!?]", text)[0].strip()

    summary_words = first_sentence.split()[:20]

    summary = " ".join(summary_words)

    if not summary:
        summary = "Note added to the knowledge base."

    return json.dumps(
        {
            "tags": significant_words,
            "summary": summary + "."
        }
    )


# ============================================================
# GEMINI REAL AI
# ============================================================

def get_ai_response(
    user_message: str,
    system_prompt: str,
) -> str:

    mock_mode = os.getenv(
        "MOCK_AI",
        "1",
    )

    if mock_mode == "1":
        return mock_ai_response(user_message)

    try:

        import google.generativeai as genai

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            print(
                "GEMINI_API_KEY is missing."
            )

            return mock_ai_response(
                user_message
            )

        genai.configure(
            api_key=api_key
        )

        model = genai.GenerativeModel(
            "gemini-1.5-flash"
        )

        prompt = (
            system_prompt
            + "\n\nUser message:\n"
            + user_message
        )

        response = model.generate_content(
            prompt
        )

        return response.text

    except Exception as e:

        print(
            "AI Error:",
            e
        )

        return mock_ai_response(
            user_message
        )


# ============================================================
# NOTE AI SUGGESTION
# ============================================================

def generate_note_suggestion(
    content: str,
):
    """
    Generate and parse AI tags + summary.
    """

    prompt = AI_PROMPT_TEMPLATE.format(
        content=content
    )

    raw_response = get_ai_response(
        user_message=content,
        system_prompt=prompt,
    )

    try:

        suggestion = json.loads(
            raw_response
        )

        if not isinstance(
            suggestion,
            dict,
        ):
            raise ValueError(
                "AI response is not a JSON object"
            )

        tags = suggestion.get(
            "tags"
        )

        summary = suggestion.get(
            "summary"
        )

        if not isinstance(
            tags,
            list,
        ):
            raise ValueError(
                "tags must be a list"
            )

        if not isinstance(
            summary,
            str,
        ):
            raise ValueError(
                "summary must be a string"
            )

        return {
            "tags": tags[:3],
            "summary": summary,
        }

    except Exception as e:

        print(
            "AI JSON Parse Error:",
            e,
        )

        print(
            "Raw AI Response:",
            raw_response,
        )

        return None