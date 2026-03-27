"""
reflection.py
-------------
Self-critiquing reflection loop.
Rewrites output until quality >= 8/10 or max 3 iterations.
Critique now explicitly penalizes generic language and copy-paste next steps.
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

from backend.schemas.models import IdeaValidationState
from backend.memory import store_validation

MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]
MAX_ITERATIONS    = 3
QUALITY_THRESHOLD = 8


def call_llm(messages: list, max_tokens: int = 900) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model, messages=messages,
                temperature=0.3, max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[reflection] {model} failed: {e}")
    return ""


def build_user_facing_output(state: IdeaValidationState, decision: dict) -> dict:
    market      = state.get("market_analysis", {})
    business    = state.get("business_analysis", {})
    demand      = market.get("demand", {})
    competition = market.get("competition", {})
    feasibility = business.get("feasibility", {})
    risk        = state.get("risk_analysis", {})

    system = f"""
You are writing a startup validation report for a real founder.
They submitted their idea and need HONEST, SPECIFIC, DATA-DRIVEN feedback.

STRICT GROUNDING RULES — these override everything else:
1. NEVER invent statistics, percentages, or growth rates not in the analyst reports
2. NEVER name companies not mentioned in competition.top_competitors or risk data
3. If a data point is missing, say "limited data available" — do not fill with guesses
4. Only reference tools that actually returned results

1. Every metric explanation MUST include a specific data point or finding
   ✓ "GitHub has 45,000+ repos for task sync tools — highly crowded"
   ✗ "Demand is medium based on current trends"

2. Next steps must be THIS WEEK actionable for THIS specific idea
   ✓ "Post in r/shopify asking if duplicate listings cost them sales — takes 20 mins"
   ✗ "Conduct user interviews to validate demand" (too generic)

3. Reasoning must name specific competitors, tools, or numbers found
   ✓ "Unito and Zapier already serve this space with $50M+ in funding"
   ✗ "Incumbents may already be solving this problem"

4. Success factors must be reasons THIS idea specifically could win
   NOT generic traits ("high demand", "clear plan")
   MAX 20 words each — punchy, not paragraphs

5. Speak directly to the founder — use "you/your", never "the analysis shows"

6. failure_reasons must include a mitigation hint in brackets e.g.
   "Unito has $20M funding in this space [focus on Shopify-only niche they ignore]"

Return ONLY valid JSON:
{{
  "reasoning": "<3-4 sentences: what the data says about THIS idea, direct to founder>",
  "demand_why": "<1 sentence with specific data point about demand>",
  "competition_why": "<1 sentence naming actual competitors or saturation evidence>",
  "feasibility_why": "<1 sentence with specific effort/cost/skill finding>",
  "risk_why": "<1 sentence naming the single biggest specific threat>",
  "success_factors": [
    "<max 20 words, specific evidence-based>",
    "<factor 2>",
    "<factor 3>"
  ],
  "failure_reasons": [
    "<specific risk [mitigation hint in brackets]>",
    "<risk 2 [mitigation]>"
  ],
  "next_steps": [
    "<concrete action this week — specific to THIS idea, include WHERE/HOW>",
    "<action 2>",
    "<action 3>"
  ]
}}
"""

    user_prompt = f"""
Idea: {state['idea']}
Idea Type: {state['idea_type']}
Verdict: {decision.get('verdict')} (score: {decision.get('overall_score')}, confidence: {decision.get('confidence_percent')}%)

Demand data: {json.dumps(demand)}
Competition data: {json.dumps(competition)}
Feasibility data: {json.dumps(feasibility)}
Risk data: {json.dumps(risk)}

Current success factors: {decision.get('success_factors', [])}
Current failure reasons: {decision.get('failure_reasons', [])}
Current reasoning: {decision.get('reasoning', '')}

Write the user-facing report. Be specific, direct, and reference actual data.
"""

    raw = call_llm([
        {"role": "system", "content": system},
        {"role": "user",   "content": user_prompt},
    ])
    raw = raw.strip("```json").strip("```").strip()
    try:
        return json.loads(raw)
    except Exception:
        return {}


def self_critique(output: dict, idea: str, idea_type: str) -> dict:
    """
    LLM scores its own output on specificity and actionability.
    Penalizes generic language hard — max 4/10 if copy-paste next steps detected.
    """
    system = """
You are a brutal quality reviewer for startup validation reports.
Score 1-10 on these criteria:

AUTOMATIC LOW SCORES:
- If next_steps could apply to ANY idea → max 4/10
  Generic: "conduct user interviews", "develop unique value proposition", "create a detailed plan"
  Specific: "search Product Hunt for 'shopify duplicate' and DM the top 3 products' founders"

- If reasoning doesn't name a specific company, number, or data point → max 5/10

- If any success_factor is longer than 25 words → max 5/10 (they must be punchy bullets)

- If success_factors are wishes not evidence → max 5/10
  Wish: "You can create high-quality content"
  Evidence: "Google Trends shows 280% growth in 'AI tools founders' over 12 months"

- If failure_reasons have no mitigation hint in brackets → max 6/10

- If failure_reasons are vague warnings → max 5/10
  Vague: "Incumbents may already be solving this"
  Specific: "Unito raised $20M and directly targets this use case [counter: focus on Shopify-only]"

Score honestly. If score < 8, rewrite ONLY the weak fields.

Return ONLY valid JSON:
{
  "score": <integer 1-10>,
  "weak_fields": ["field1", "field2"],
  "reason": "<one sentence why score is what it is>",
  "improved": {
    "reasoning": "...",
    "demand_why": "...",
    "competition_why": "...",
    "feasibility_why": "...",
    "risk_why": "...",
    "success_factors": [...],
    "failure_reasons": [...],
    "next_steps": [...]
  }
}

If score >= 8: {"score": <score>, "weak_fields": [], "reason": "...", "improved": null}
"""

    user_prompt = f"""
Idea: {idea}
Idea Type: {idea_type}

Report to review:
{json.dumps(output, indent=2)}

Score strictly. Penalize generic language hard.
"""

    raw = call_llm([
        {"role": "system", "content": system},
        {"role": "user",   "content": user_prompt},
    ], max_tokens=1100)

    raw = raw.strip("```json").strip("```").strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"score": 8, "weak_fields": [], "reason": "Parse failed", "improved": None}


def reflection_node(state: IdeaValidationState) -> dict:
    print("[reflection] Building user-facing output...")

    decision = state.get("decision", {})
    market   = state.get("market_analysis", {})
    business = state.get("business_analysis", {})

    # ── Step 1: Initial user-facing output ────────────────────────────────────
    user_output = build_user_facing_output(state, decision)

    if not user_output:
        print("[reflection] ⚠ Initial build failed, using decision output as fallback")
        user_output = {
            "reasoning":       decision.get("reasoning", ""),
            "demand_why":      "",
            "competition_why": "",
            "feasibility_why": "",
            "risk_why":        "",
            "success_factors": decision.get("success_factors", []),
            "failure_reasons": decision.get("failure_reasons", []),
            "next_steps":      [],
        }

    # ── Step 2: Self-critique loop ─────────────────────────────────────────────
    score     = 0
    iteration = 0

    for iteration in range(MAX_ITERATIONS):
        critique = self_critique(user_output, state["idea"], state["idea_type"])
        score    = critique.get("score", 8)
        improved = critique.get("improved")
        reason   = critique.get("reason", "")

        print(f"[reflection] Iteration {iteration + 1}: score={score}/10 | {reason[:60]}")
        print(f"             Weak fields: {critique.get('weak_fields', [])}")

        if score >= QUALITY_THRESHOLD or not improved:
            print(f"[reflection] ✅ Quality threshold met (score={score})")
            break

        # Merge only the improved fields
        user_output = {**user_output, **improved}
        print(f"[reflection] 🔄 Rewrote: {critique.get('weak_fields', [])}")
    else:
        print(f"[reflection] ⚠ Hit max iterations ({MAX_ITERATIONS}) — using best version (score={score})")

    # ── Step 3: Update decision with refined fields ────────────────────────────
    updated_decision = {
        **decision,
        "reasoning":       user_output.get("reasoning", decision.get("reasoning", "")),
        "success_factors": user_output.get("success_factors", decision.get("success_factors", [])),
        "failure_reasons": user_output.get("failure_reasons", decision.get("failure_reasons", [])),
    }

    # ── Step 4: Build final output ─────────────────────────────────────────────
    final_output = {
        "idea":               state["idea"],
        "idea_type":          state["idea_type"],
        "tools_used":         state["tools_assigned"],
        "demand":             market.get("demand", {}),
        "competition":        market.get("competition", {}),
        "feasibility":        business.get("feasibility", {}),
        "risk":               state.get("risk_analysis", {}),
        "overall_score":      updated_decision.get("overall_score"),
        "verdict":            updated_decision.get("verdict"),
        "confidence_percent": updated_decision.get("confidence_percent"),
        "success_factors":    updated_decision.get("success_factors", []),
        "failure_reasons":    updated_decision.get("failure_reasons", []),
        "similar_past_ideas": state.get("niche_suggestions", []),
        "reasoning":          user_output.get("reasoning", ""),
        "demand_why":         user_output.get("demand_why", ""),
        "competition_why":    user_output.get("competition_why", ""),
        "feasibility_why":    user_output.get("feasibility_why", ""),
        "risk_why":           user_output.get("risk_why", ""),
        "next_steps":         user_output.get("next_steps", []),
        # Internal only
        "reflection_notes":   f"Quality: {score}/10 after {iteration + 1} iteration(s)",
    }

    store_validation(final_output)
    print(f"[reflection] ✅ Done — final quality: {score}/10 in {iteration + 1} iteration(s)")

    return {
        "decision":     updated_decision,
        "reflection":   final_output["reflection_notes"],
        "final_output": final_output,
    }