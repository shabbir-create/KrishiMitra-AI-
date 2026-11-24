"""
KrishiMitra AI - Agricultural Assistant
========================================

LLM-based bilingual agricultural assistant using OpenRouter API.

Features:
- English questions
- Hindi questions
- Agricultural advice
- OpenRouter LLM
- Local FAQ fallback if API fails
- Safe API-key loading from project .env file
"""

import os
import re
import unicodedata
import json
from pathlib import Path

import requests
from dotenv import load_dotenv


# ============================================================
# PROJECT PATHS
# ============================================================

# assistant.py location:
#
# D:\KrishiMitra-AI-Starter\KrishiMitra-AI\backend\assistant.py

BACKEND_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = BACKEND_DIR.parent


# Full expected .env path:
#
# D:\KrishiMitra-AI-Starter\KrishiMitra-AI\.env

ENV_FILE = PROJECT_ROOT / ".env"


# Load environment variables explicitly from project root
load_dotenv(dotenv_path=ENV_FILE)


# ============================================================
# OPENROUTER CONFIGURATION
# ============================================================

def openrouter_model():
    return os.getenv("OPENROUTER_MODEL", "openrouter/free")


OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


# ============================================================
# FAQ FILE
# ============================================================

FAQ_FILE = (
    BACKEND_DIR
    / "knowledge"
    / "agriculture_faq.json"
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are KrishiMitra AI, an intelligent agricultural assistant
designed to help farmers.

Your main purpose is to provide simple, practical and responsible
agricultural guidance.

You can help with:

- Crop diseases
- Plant symptoms
- Leaf diseases
- Irrigation
- Soil health
- Fertilizers
- Nutrient deficiencies
- Crop management
- Pest symptoms
- Plant care
- Farming practices
- Disease prevention
- Basic agricultural guidance


LANGUAGE RULES:

1. If the selected language is Hindi, answer completely in Hindi.

2. If the selected language is English, answer completely in English.

3. Use simple language that farmers can understand.


AGRICULTURAL SAFETY RULES:

1. Do not confidently diagnose a crop disease when the symptoms
   are insufficient.

2. Mention possible causes when there can be multiple explanations.

3. When a leaf image is needed for better identification, tell
   the farmer to use the KrishiMitra AI Disease Detection feature.

4. Do not recommend dangerous or excessive pesticide,
   insecticide or fungicide doses.

5. Do not invent pesticide dosages.

6. If chemical treatment may be required, recommend checking
   the crop-approved product label and local agricultural
   recommendations.

7. Encourage farmers to verify important treatment decisions
   with a KVK, agricultural extension officer or qualified
   agricultural expert.


ANSWER FORMAT:

When appropriate, structure the answer using:

Possible Cause:
Symptoms to Check:
What You Can Do:
Prevention:

However, do not force this structure when a short direct answer
is more appropriate.

Keep most responses concise and practical.


SCOPE:

You are an agriculture-focused assistant.

If the user asks something completely unrelated to agriculture,
politely explain that KrishiMitra AI is designed for agriculture
and farming-related questions.
"""


# ============================================================
# LOAD LOCAL FAQ
# ============================================================

def load_faq():
    """
    Load agriculture_faq.json.

    Returns:
        list: FAQ entries
    """

    if not FAQ_FILE.is_file():
        return []

    try:

        with open(
            FAQ_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

    except Exception as error:

        print(
            "FAQ loading error:",
            error
        )

    return []


# ============================================================
# FAQ FALLBACK
# ============================================================

def faq_fallback(
    question: str,
    language: str = "en"
):
    """
    Search local FAQ if OpenRouter is unavailable.
    """

    normalized = " ".join(unicodedata.normalize("NFC", question).casefold().split())
    best_answer = None
    best_length = 0
    field = "answer_hi" if language.lower().startswith("hi") else "answer_en"
    for entry in load_faq():
        for keyword in entry["keywords"]:
            phrase = unicodedata.normalize("NFC", keyword).casefold()
            if len(phrase) <= best_length:
                continue
            if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", normalized):
                best_answer = entry[field]
                best_length = len(phrase)
    return best_answer


# ============================================================
# ASK OPENROUTER
# ============================================================

def ask_openrouter(
    question: str,
    language: str = "en"
):
    """
    Send agricultural question to OpenRouter API.

    Returns:
        str: AI generated answer
    """


    # --------------------------------------------------------
    # CHECK API KEY
    # --------------------------------------------------------

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:

        raise RuntimeError(
            f"OPENROUTER_API_KEY not found. "
            f"Expected .env file at: {ENV_FILE}"
        )


    # --------------------------------------------------------
    # LANGUAGE INSTRUCTION
    # --------------------------------------------------------

    hindi = (
        str(language)
        .lower()
        .startswith("hi")
    )


    if hindi:

        language_instruction = """
उत्तर पूरी तरह हिंदी में दें।
सरल और किसान-अनुकूल भाषा का उपयोग करें।
"""

    else:

        language_instruction = """
Answer completely in English.
Use simple farmer-friendly language.
"""


    # --------------------------------------------------------
    # USER PROMPT
    # --------------------------------------------------------

    user_prompt = f"""
{language_instruction}

Farmer Question:

{question}
"""


    # --------------------------------------------------------
    # HEADERS
    # --------------------------------------------------------

    headers = {

        "Authorization":
            f"Bearer {api_key}",

        "Content-Type":
            "application/json",

        "X-Title":
            "KrishiMitra AI"
    }


    # --------------------------------------------------------
    # REQUEST BODY
    # --------------------------------------------------------

    payload = {

        "model":
            openrouter_model(),

        "messages": [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT
            },

            {
                "role":
                    "user",

                "content":
                    user_prompt
            }

        ],

        "temperature":
            0.3,

        "max_tokens":
            600

    }


    # --------------------------------------------------------
    # API REQUEST
    # --------------------------------------------------------

    response = requests.post(

        OPENROUTER_URL,

        headers=headers,

        json=payload,

        timeout=45

    )


    # Raise error for 4xx / 5xx responses

    response.raise_for_status()


    data = response.json()


    # --------------------------------------------------------
    # VALIDATE RESPONSE
    # --------------------------------------------------------

    if "choices" not in data:

        raise RuntimeError(
            f"Invalid OpenRouter response: {data}"
        )


    if not data["choices"]:

        raise RuntimeError(
            "OpenRouter returned no response choices."
        )


    message = (
        data["choices"][0]
        .get("message", {})
    )


    answer = message.get(
        "content",
        ""
    )


    if not isinstance(answer, str) or not answer.strip():

        raise RuntimeError(
            "OpenRouter returned an empty answer."
        )


    return answer.strip()


# ============================================================
# MAIN FUNCTION
# ============================================================

def answer_question(
    question: str,
    language: str = "en"
):
    """
    Main function used by FastAPI.

    Flow:

    Question
        ↓
    OpenRouter
        ↓
    AI response

    If OpenRouter fails:
        ↓
    Local FAQ

    If FAQ also fails:
        ↓
    Basic fallback response
    """


    question = str(
        question or ""
    ).strip()


    language = str(
        language or "en"
    ).lower()


    hindi = language.startswith(
        "hi"
    )


    # --------------------------------------------------------
    # EMPTY QUESTION
    # --------------------------------------------------------

    if not question:

        if hindi:

            answer = (
                "कृपया अपना खेती से संबंधित सवाल लिखें।"
            )

        else:

            answer = (
                "Please enter your farming question."
            )


        return {

            "intent":
                "empty_question",

            "answer":
                answer,

            "source":
                "local"

        }


    # ========================================================
    # TRY OPENROUTER
    # ========================================================

    provider_status = "not_configured"
    if os.getenv("OPENROUTER_API_KEY", "").strip():
        try:
            ai_answer = ask_openrouter(question=question, language=language)
            return {
                "intent": "ai_agriculture",
                "answer": ai_answer,
                "source": "openrouter",
                "model": openrouter_model(),
            }
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            print("OpenRouter returned HTTP", status)
            provider_status = "provider_error"
        except (requests.RequestException, RuntimeError, ValueError, TypeError, AttributeError) as exc:
            print("OpenRouter request failed:", type(exc).__name__)
            provider_status = "provider_error"

    local_answer = faq_fallback(

        question=question,

        language=language

    )


    if local_answer:

        return {

            "intent":
                "agriculture_faq",

            "answer":
                local_answer,

            "source":
                "local_faq",
            "provider_status": provider_status,

        }


    # ========================================================
    # FINAL FALLBACK
    # ========================================================

    return {
        "intent": "topic_uncovered",
        "source": "local",
        "provider_status": provider_status,
        "answer": (
            "इस सवाल के लिए अंतर्निहित मार्गदर्शिका में जानकारी नहीं है। आप सिंचाई, पीली पत्तियों, पछेती झुलसा, मिट्टी की सेहत या खाद के बारे में पूछ सकते हैं।"
            if hindi else
            "The built-in guide doesn’t cover this question. It can help with irrigation, yellowing leaves, late blight, soil health and fertilizer. Choose a sample question or ask about one of those topics."
        ),
    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Project root:",
        PROJECT_ROOT
    )

    print(
        "ENV file:",
        ENV_FILE
    )

    print(
        "API key loaded:",
        bool(os.getenv("OPENROUTER_API_KEY"))
    )

    print(
        "Model:",
        openrouter_model()
    )


    result = answer_question(

        "Why are my tomato leaves turning yellow?",

        "en"

    )


    print("\nRESULT:\n")

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )
