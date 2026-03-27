"""
competition_analyst.py — LangGraph node
Grounded version: only names competitors actually found in research data.
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

from backend.schemas.models import IdeaValidationState

MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]

SYSTEM_PROMPT = """
You are a competition analyst. Identify competitors using ONLY data explicitly found.

CRITICAL GROUNDING RULES:
1. Only name competitors explicitly mentioned in the research data
2. Do NOT name companies from your training data - only cite what tools found
3. If no competitors found in data, say so clearly and set level="low"
4. Add source attribution: where did each competitor come from?
5. saturation_score is ONLY based on actual competitor count found:
   - 0 competitors found → saturation_score=1-2
   - 1-2 found → saturation_score=3-4
   - 3-5 found → saturation_score=5-6
   - 6-10 found → saturation_score=7-8
   - 10+ found → saturation_score=8-10

Do NOT cite competitors from your general knowledge - ONLY from the data provided.

Return ONLY valid JSON:
{
  "level": "high" | "medium" | "low",
  "competitors_found": <count of actual competitors in data>,
  "top_competitors": ["<only names from actual data>"],
  "saturation_score": <integer 1-10 based on actual count>,
  "data_sources": "<where competitors came from: GitHub repos, Product Hunt, web search, etc>",
  "confidence": "high" | "medium" | "low",
  "notes": "<what was actually found - be specific or say 'no competitors found'>"
}
"""


def _extract_competitors(research_data: dict) -> tuple[str, int]:
    """Extract competitor data from research. Returns (text, competitor_count)."""
    found = []
    competitor_count = 0

    tavily = research_data.get("tavily", [])
    if tavily:
        found.append(f"WEB SEARCH found {len(tavily)} results:")
        for r in tavily[:5]:
            found.append(f"  - {r.get('title','')[:80]}")
            competitor_count += 1

    ph = research_data.get("product_hunt", [])
    if ph:
        found.append(f"\nPRODUCT HUNT found {len(ph)} products:")
        for r in ph[:5]:
            found.append(f"  - {r.get('title','')[:80]}")
            competitor_count += 1

    github = research_data.get("github", {})
    repos = github.get("top_repos", [])
    if repos:
        found.append(f"\nGITHUB found {github.get('total_count', 0)} repositories, top ones:")
        for r in repos[:5]:
            found.append(f"  - {r.get('name','')} ({r.get('stars',0)} stars)")
            competitor_count += 1

    if not found:
        return "No competitor data found in any search tool - 0 results returned.", 0
    
    return "\n".join(found), min(competitor_count, 10)  # Cap at 10 for scoring


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
                temperature=0.1,
                max_tokens=400,
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.strip("```json").strip("```").strip()
            result = json.loads(raw)
            if result.get("level") not in ["high", "medium", "low"]:
                result["level"] = "low" if result.get("competitors_found", 0) == 0 else "medium"
            if not isinstance(result.get("saturation_score"), (int, float)):
                result["saturation_score"] = 2
            if not isinstance(result.get("competitors_found"), int):
                result["competitors_found"] = len(result.get("top_competitors", []))
            result["saturation_score"] = max(1, min(10, int(result["saturation_score"])))
            if result.get("confidence") not in ["high", "medium", "low"]:
                result["confidence"] = "medium"
            return result
        except Exception as e:
            print(f"[competition_analyst] {model} failed: {e}")
    return {
        "level": "low",
        "competitors_found": 0,
        "top_competitors": [],
        "saturation_score": 1,
        "data_sources": "Analysis failed",
        "confidence": "low",
        "notes": "Unable to analyze competition data"
    }


def competition_analyst_node(state: IdeaValidationState) -> dict:
    competitor_data, count = _extract_competitors(state.get("research_data", {}))
    prompt = f"""
Idea: {state['idea']}
Idea Type: {state['idea_type']}

ACTUAL COMPETITOR DATA FOUND ({count} items):
{competitor_data}

IMPORTANT: Only name competitors that appear above. If no data above, saturation_score should be 1-2.
Count the actual items found and set saturation_score accordingly.
Do NOT use your general knowledge to add competitors.
"""
    print(f"[competition_analyst] Analyzing competition ({count} items found)...")
    result = call_llm(prompt)
    print(f"[competition_analyst] ✅ Done — level: {result.get('level')}, saturation: {result.get('saturation_score')}, confidence: {result.get('confidence')}")
    return {"market_analysis": {"competition": result}}