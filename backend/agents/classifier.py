import json
import re
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

from backend.schemas.models import IdeaValidationState, IDEA_TYPES, TOOLS_MAPPING

# Updated model list — llama3-70b-8192 is decommissioned
MODELS = [
    "llama-3.3-70b-versatile",   # best available on Groq right now
    "llama-3.1-8b-instant",      # fast fallback
    "gemma2-9b-it",              # last resort
]

SYSTEM_PROMPT = """
You are an idea classification expert. Your only job is to read a user's idea
and classify it into EXACTLY ONE of these 6 categories:

  1. business         – a product/service company, brand, or marketplace
  2. dev_project      – a software library, app, tool, API, or developer utility
  3. research         – an academic study, scientific experiment, or paper topic
  4. content          – a YouTube channel, podcast, blog, newsletter, or media brand
  5. physical_product – a manufactured item, hardware device, or consumer good
  6. social_impact    – an NGO, charity, community initiative, or social enterprise

Rules:
- Reply ONLY with valid JSON. No extra text, no markdown, no explanation.
- JSON format: {"idea_type": "<category>", "reason": "<one short sentence>"}
- The "idea_type" value must be one of the 6 exact strings above.
- When in doubt between two categories, pick the more specific one.
"""


def call_with_fallback(client: Groq, messages: list) -> str:
    last_error = None
    for model in MODELS:
        try:
            print(f"[classifier] Trying model: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=100,
            )
            print(f"[classifier] Success with: {model}")
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[classifier] Model {model} failed: {e}")
            last_error = e
            continue
    raise RuntimeError(f"All models failed. Last error: {last_error}")


def parse_idea_type(raw_text: str) -> str:
    clean = re.sub(r"```(?:json)?", "", raw_text).strip("` \n")
    try:
        parsed    = json.loads(clean)
        idea_type = parsed.get("idea_type", "").strip().lower()
    except json.JSONDecodeError:
        idea_type = ""
        for t in IDEA_TYPES:
            if t in clean.lower():
                idea_type = t
                break
    if idea_type not in IDEA_TYPES:
        print(f"[classifier] Unknown type '{idea_type}', defaulting to 'business'")
        idea_type = "business"
    return idea_type


def classifier_node(state: IdeaValidationState) -> dict:
    client   = Groq(api_key=os.getenv("GROQ_API_KEY"))
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": f"Idea: {state['idea']}"},
    ]
    raw_text  = call_with_fallback(client, messages)
    idea_type = parse_idea_type(raw_text)
    tools     = TOOLS_MAPPING.get(idea_type, [])
    return {
        "idea_type":      idea_type,
        "tools_assigned": tools,
    }