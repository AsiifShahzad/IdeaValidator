"""
risk_analyst.py — LangGraph node
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

from backend.schemas.models import IdeaValidationState

MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]

SYSTEM_PROMPT = """
You are a risk analyst. Identify the top 3 contextual risks.

Risks must be specific to the idea_type:
- dev_project      → incumbents, low monetization, dev abandonment
- business         → high CAC, regulatory risk, supply chain
- research         → funding availability, replication crisis, ethical approval
- content          → algorithm changes, audience fatigue, monetization dependency
- physical_product → manufacturing defects, import tariffs, counterfeit competition
- social_impact    → donor dependency, mission drift, volunteer burnout

IMPORTANT: level must ALWAYS be exactly "high", "medium", or "low". Never "unknown".

Return ONLY valid JSON:
{
  "level": "high" | "medium" | "low",
  "top_risks": [
    {"risk": "<name>", "explanation": "<one sentence why>"},
    {"risk": "<name>", "explanation": "<one sentence why>"},
    {"risk": "<name>", "explanation": "<one sentence why>"}
  ]
}
"""


def call_llm(prompt: str) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
                temperature=0.2,
                max_tokens=400,
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.strip("```json").strip("```").strip()
            result = json.loads(raw)
            if result.get("level", "") not in ["high", "medium", "low"]:
                result["level"] = "medium"
            return result
        except Exception as e:
            print(f"[risk_analyst] {model} failed: {e}")
    return {"level": "medium", "top_risks": []}


def risk_analyst_node(state: IdeaValidationState) -> dict:
    prompt = f"""
Idea: {state['idea']}
Idea Type: {state['idea_type']}
Research Data: {json.dumps(state['research_data'], indent=2)[:3000]}

Identify top 3 risks. Return level as exactly "high", "medium", or "low".
"""
    print("[risk_analyst] Analyzing risks...")
    result = call_llm(prompt)
    print(f"[risk_analyst] ✅ Done — level: {result.get('level')}")
    return {"risk_analysis": result}