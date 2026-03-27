import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
from backend.schemas.models import IdeaValidationState
from backend.memory import search_similar_ideas

MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]

SCORING_ANCHORS = """
SCORE CALIBRATION — use these as strict anchors, do not cluster around 6-7:

  9-10 → Multiple strong signals: proven demand (real numbers), low competition,
          clear monetization, large addressable market with evidence
  7-8  → Good signals, manageable competition, viable path, some data backing
  5-6  → Mixed signals — real risks but not fatal, needs validation before building
  3-4  → Weak demand OR dominant incumbents with no differentiation angle found
  1-2  → No demand evidence, fully saturated market, unclear revenue path

CONTRADICTION RULE:
  If competition saturation_score <= 3 BUT risks mention "incumbents" → CONTRADICTION
  If demand is "high" BUT competition saturation >= 8 → CONTRADICTION
  You MUST flag any contradiction in failure_reasons and adjust score accordingly.
  A contradicted metric cannot support a high score.

SPECIFICITY RULE:
  success_factors and failure_reasons MUST reference actual data found:
  ✓ "GitHub shows 45,000 similar repos indicating crowded space"
  ✓ "npm downloads for related packages grew 34% last quarter"  
  ✗ "High demand for this type of tool" (too generic — rejected)
  ✗ "You should develop a unique value proposition" (advice, not evidence)

NEVER return 6.5 unless data is genuinely split. Round to nearest 0.5.
"""


def detect_contradictions(market: dict, risk: dict) -> list[str]:
    """Rule-based contradiction detection before sending to LLM."""
    contradictions = []
    competition  = market.get("competition", {})
    demand       = market.get("demand", {})
    risk_data    = risk

    sat_score = competition.get("saturation_score", 5)
    risk_text = json.dumps(risk_data).lower()

    if sat_score <= 3 and "incumbent" in risk_text:
        contradictions.append(
            f"CONTRADICTION: Competition saturation={sat_score}/10 (low) but risks mention incumbents — re-evaluate competition level"
        )

    if demand.get("level") == "high" and sat_score >= 8:
        contradictions.append(
            "CONTRADICTION: Demand is high but market is nearly saturated (8+/10) — high demand in saturated market needs differentiation strategy"
        )

    return contradictions


def build_prompt(state: IdeaValidationState, similar_summary: str, contradictions: list) -> str:
    market   = state.get("market_analysis", {})
    business = state.get("business_analysis", {})

    contradiction_block = ""
    if contradictions:
        contradiction_block = "\n--- DETECTED CONTRADICTIONS (MUST ADDRESS) ---\n"
        contradiction_block += "\n".join(f"⚠ {c}" for c in contradictions)

    return f"""
Idea: {state['idea']}
Idea Type: {state['idea_type']}
Tools Used: {state['tools_assigned']}

--- SIMILAR PAST {state['idea_type'].upper()} IDEAS FROM MEMORY ---
{similar_summary}

--- ANALYST REPORTS ---
DEMAND:
{json.dumps(market.get('demand', {}), indent=2)}

COMPETITION:
{json.dumps(market.get('competition', {}), indent=2)}

RISK:
{json.dumps(state.get('risk_analysis', {}), indent=2)}
{contradiction_block}

Produce your verdict now. Every factor must cite specific data from the reports above.
"""


def call_llm(state: IdeaValidationState, similar_summary: str, contradictions: list) -> dict:
    system_prompt = f"""
You are a hard-nosed startup analyst validating a {state['idea_type']} idea.
You have a reputation for honest, data-driven verdicts — not feel-good generic advice.

{SCORING_ANCHORS}

Tools that were used to collect data: {state['tools_assigned']}
Use the actual data from these tools in your reasoning — not generic statements.

Return ONLY valid JSON:
{{
  "overall_score": <float, NOT 6.5 unless genuinely split>,
  "verdict": "GO" | "NO GO" | "MAYBE",
  "confidence_percent": <integer>,
  "success_factors": [
    "<specific evidence-backed factor with data reference>",
    "<factor 2>",
    "<factor 3>"
  ],
  "failure_reasons": [
    "<specific risk with contradiction flag if any>",
    "<risk 2>"
  ],
  "reasoning": "<2-3 sentences citing actual numbers and findings, written directly to the founder>"
}}
"""
    client     = Groq(api_key=os.getenv("GROQ_API_KEY"))
    last_error = None

    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": build_prompt(state, similar_summary, contradictions)},
                ],
                temperature=0.2,
                max_tokens=700,
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.strip("```json").strip("```").strip()
            return json.loads(raw)
        except Exception as e:
            print(f"[decision] Model {model} failed: {e}")
            last_error = e
            continue

    print(f"[decision] All models failed: {last_error}")
    return {
        "overall_score":      0,
        "verdict":            "MAYBE",
        "confidence_percent": 0,
        "success_factors":    [],
        "failure_reasons":    [],
        "reasoning":          "Decision analysis failed.",
    }


def decision_node(state: IdeaValidationState) -> dict:
    print("[decision] Checking for metric contradictions...")
    market   = state.get("market_analysis", {})
    contradictions = detect_contradictions(market, state.get("risk_analysis", {}))
    if contradictions:
        for c in contradictions:
            print(f"[decision] ⚠ {c}")

    print("[decision] Searching memory for similar ideas...")
    similar         = search_similar_ideas(state["idea"], state["idea_type"])
    similar_summary = "\n".join(
        f'- "{s["idea"][:80]}" → {s["verdict"]} (score:{s["score"]}, similarity:{s["similarity"]})'
        for s in similar
    ) if similar else "No similar past ideas found."

    print("[decision] Generating verdict...")
    result = call_llm(state, similar_summary, contradictions)
    print(f"[decision] ✅ verdict: {result.get('verdict')} | score: {result.get('overall_score')} | confidence: {result.get('confidence_percent')}%")

    return {
        "decision":          result,
        "niche_suggestions": similar,
    }