"""
decision.py IMPROVEMENTS — Better Verdict Calibration
===================================================

The key insight is that "NO GO" verdicts are too harsh.

OLD LOGIC (Wrong):
- low demand → NO GO (ignores if market is GROWING)
- high competition → harshly penalizes (ignores if space is valuable)
- Result: 5 out of 6 ideas get NO GO

NEW LOGIC (Better):
- Account for market GROWTH, not just current demand
- Consider: Is there OPPORTUNITY even if competition exists?
- Be more generous with MAYBE verdicts
- Save NO GO only for truly problematic ideas

Verdict Rules:
- GO (7-10): Strong demand + low competition OR growing market + clear differentiation
- MAYBE (4-7): Mixed signals, needs more work but viable path exists
- NO GO (1-3): No demand signals + high competition OR fundamentally flawed

Score Calibration:
- Raw Demand (0-10): Based on data sources found and signals strength
- Raw Competition (0-10): Based on saturation and incumbent strength
- Growth Bonus (0-3): If market is rising, add points
- Differentiation Bonus (0-3): If founder can articulate niche
- Risk Penalty (0-5): Subtract for high risks

Final Score = Min(Raw_Demand + Raw_Competition)/2 + Growth_Bonus - Risk_Penalty
Result: More GO/MAYBE, fewer NO GO
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
from backend.schemas.models import IdeaValidationState
from backend.memory import search_similar_ideas

MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]

SCORING_ANCHORS = """
IMPROVED SCORE CALIBRATION — accounting for market trends

SCORING FRAMEWORK:
  10  → Strong demand + low competition + clear monetization + large market
  8-9 → Good demand OR growing market with low competition
  6-7 → Mixed signals but viable path OR strong niche opportunity
  5   → Borderline — could go either way, needs more research
  3-4 → Weak demand OR saturated market with weak differentiation
  1-2 → No demand signals + high competition OR fundamentally unviable

KEY RULE: Market Growth Matters
- If Google Trends shows rising interest but current demand is "low"
  → This is opportunity, not a weakness
  → Score should reflect future potential, not just current state
  → Raise from 3-4 to 5-6 range

KEY RULE: Competition Needs Context
- Competition saturation=8 in a huge market (e.g., e-commerce) is different from saturation=8 in tiny niche
  → Do not auto-penalize high saturation without context
  → "Competition: high, but Google Trends +25% growth" = OPPORTUNITY

VERDICT MAPPING:
  Score 8-10 → "GO" (strong signals, clear path to validation)
  Score 5-7  → "MAYBE" (mixed signals, needs founder to narrow focus/validate)
  Score 1-4  → "NO GO" (fundamental blockers or no market evidence)

DO NOT return 6.5 unless data is genuinely 50/50 split.

CONTRADICTION DETECTION:
  If Demand="high" AND Competition="high" AND Growth="rising"
    → This is a GOOD problem! Not a contradiction.
    → These markets attract competition BECAUSE they're growing
    → Factor: "High competition in growing market - opportunity for differentiation"

  If Demand="low" AND Competition="low" AND NO growth signals
    → This is bad - niche is small and stagnant
    → Factor: "Small, stagnant market - limited upside"

  If Demand="low" AND Competition="high"
    → Bad - why do competitors do well if demand is low?
    → This IS a contradiction - investigate further
    → Advice: "Data conflict - more research needed on who's buying"
"""

def detect_contradictions(market: dict, risk: dict, state: dict) -> list[str]:
    """Improved contradiction detection that accounts for market dynamics."""
    contradictions = []
    competition  = market.get("competition", {})
    demand       = market.get("demand", {})
    
    demand_level = demand.get("level", "medium")
    demand_trend = demand.get("trend_direction", "unknown")
    comp_level = competition.get("level", "medium")
    sat_score = competition.get("saturation_score", 5)

    # Growth in competitive market is OPPORTUNITY, not contradiction
    if demand_level == "high" and sat_score >= 8 and demand_trend == "rising":
        contradictions.append(
            "✓ GOOD SIGNAL: Growing demand in competitive market = opportunity for differentiation [focus on underserved segment]"
        )
    
    # Low demand with high competition is a real contradiction
    if demand_level == "low" and sat_score >= 8:
        contradictions.append(
            "⚠ CONTRADICTION: Low demand but high competition - unclear why competitors exist [needs investigation: Are they pivoting? Is data wrong?]"
        )
    
    # Low demand with rising trend is actually opportunity
    if demand_level == "low" and demand_trend == "rising":
        contradictions.append(
            "✓ GOOD SIGNAL: Low current demand but rising trend = early-stage opportunity [time-sensitive: first-mover advantage]"
        )
    
    return contradictions


def build_improved_prompt(state: IdeaValidationState, similar_summary: str, contradictions: list) -> str:
    market   = state.get("market_analysis", {})
    business = state.get("business_analysis", {})
    demand   = market.get("demand", {})
    competition = market.get("competition", {})
    risk = state.get("risk_analysis", {})

    contradiction_block = ""
    if contradictions:
        contradiction_block = "\n--- MARKET INSIGHTS (IMPORTANT) ---\n"
        contradiction_block += "\n".join(contradictions)

    return f"""
Idea: {state['idea']}
Idea Type: {state['idea_type']}
Tools Used: {state['tools_assigned']}

DATA QUALITY NOTES:
- Demand confidence: {demand.get('confidence', 'unknown')} (based on {demand.get('data_sources_found', 0)} data sources)
- Competition confidence: {competition.get('confidence', 'unknown')} (found {competition.get('competitors_found', 0)} competitors)
- Risk level: {risk.get('level', 'unknown')}

{contradiction_block}

--- ANALYST REPORTS ---
DEMAND: {json.dumps(demand, indent=2)}
COMPETITION: {json.dumps(competition, indent=2)}
RISK: {json.dumps(risk, indent=2)}

SIMILAR PAST IDEAS:
{similar_summary}

Use the improved scoring framework. Account for growth trends.
Generate a verdict that is encouraging but realistic.
"""


def call_llm(state: IdeaValidationState, similar_summary: str, contradictions: list) -> dict:
    system_prompt = f"""
You are a startup analyst validating a {state['idea_type']} idea.
Your job is to be honest but encouraging - help founders see opportunities, not just roadblocks.

{SCORING_ANCHORS}

Tools actually used: {state['tools_assigned']}
Reference the real data from these tools in your reasoning.

TONE: Direct, specific, data-driven - not generic encouragement.

Return ONLY valid JSON:
{{
  "overall_score": <float 1-10, reflect market trends not just current state>,
  "verdict": "GO" | "NO GO" | "MAYBE",
  "confidence_percent": <integer: how confident in this verdict given data quality>,
  "success_factors": [
    "<specific advantage backed by data>",
    "<factor 2>",
    "<factor 3>"
  ],
  "failure_reasons": [
    "<specific risk with data backing - include [mitigation] hint>",
    "<risk 2 [mitigation]>"
  ],
  "reasoning": "<2-3 sentences to founder: what our data saying + why this verdict>"
}}
"""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": build_improved_prompt(state, similar_summary, contradictions)},
                ],
                temperature=0.2,
                max_tokens=800,
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.strip("```json").strip("```").strip()
            result = json.loads(raw)
            
            # Validate
            if result.get("overall_score"):
                result["overall_score"] = max(1, min(10, float(result["overall_score"])))
            if result.get("verdict") not in ["GO", "NO GO", "MAYBE"]:
                result["verdict"] = "MAYBE"
            if result.get("confidence_percent"):
                result["confidence_percent"] = max(0, min(100, int(result["confidence_percent"])))
            
            return result
        except Exception as e:
            print(f"[decision] {model} failed: {e}")
    
    return {
        "overall_score": 5,
        "verdict": "MAYBE",
        "confidence_percent": 30,
        "success_factors": [],
        "failure_reasons": ["Analysis failed"],
        "reasoning": "Unable to complete analysis",
    }


def decision_node(state: IdeaValidationState) -> dict:
    print("[decision] Detecting market dynamics and contradictions...")
    market   = state.get("market_analysis", {})
    contradictions = detect_contradictions(market, state.get("risk_analysis", {}), state)
    
    if contradictions:
        for c in contradictions:
            print(f"[decision] {c}")

    print("[decision] Searching for similar past ideas...")
    similar         = search_similar_ideas(state["idea"], state["idea_type"])
    similar_summary = "\n".join(
        f'- "{s["idea"][:80]}" → {s["verdict"]} (score:{s["score"]}, similarity:{s["similarity"]})'
        for s in similar
    ) if similar else "No similar past ideas in database."

    print("[decision] Generating improved verdict...")
    result = call_llm(state, similar_summary, contradictions)
    print(f"[decision] ✅ verdict: {result.get('verdict')} | score: {result.get('overall_score')}/10 | confidence: {result.get('confidence_percent')}%")

    return {
        "decision":          result,
        "niche_suggestions": similar,
    }
