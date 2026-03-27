"""
demand_analyst.py — LangGraph node
Improved version: Prevents hallucination with data confidence scoring.
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

from backend.schemas.models import IdeaValidationState

MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]

SYSTEM_PROMPT = """
You are a demand analyst. Estimate demand using ONLY the research data provided.

CRITICAL GROUNDING RULES:
1. NEVER invent statistics, percentages, or growth figures not explicitly in the data
2. NEVER cite companies, products, or metrics not found by the search tools
3. If most tools returned empty/zero results, set level="low" and confidence="low"
4. NEVER claim "evidence" from tools that returned empty data

Demand level guide (ONLY based on real signals):
- high:   Multiple data sources show interest (3+ tools with results, numbers >1000, rising trends)
- medium: Some signals present but incomplete (1-2 tools with results, mixed trends)
- low:    Weak signals or empty results (0-1 tools returned data, or all show 0)

Tools and what counts as a signal:
- GitHub: total_count > 100 with recent activity = strong signal
- npm: >1000 downloads/month = strong signal; if 0 = no signal
- Product Hunt: 5+ products found = signal
- Google Trends: direction="rising" AND peak>50 = strong signal
- Tavily/News: 3+ relevant results = signal

IMPORTANT: If a tool shows "0 results" or "no data", do NOT estimate or guess. Say so.

Return ONLY valid JSON - NO EXCEPTIONS:
{
  "level": "high" | "medium" | "low",
  "data_sources_found": <number of tools that returned actual data>,
  "confidence": "high" | "medium" | "low",
  "evidence": "<specific numbers and tool names ONLY if data exists, or 'Insufficient data from tools'>",
  "trend_direction": "rising" | "stable" | "declining" | "unknown",
  "requires_manual_research": <true if confidence is low>
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
                temperature=0.1,
                max_tokens=400,
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.strip("```json").strip("```").strip()
            result = json.loads(raw)
            
            # Validate response structure
            if result.get("level") not in ["high", "medium", "low"]:
                result["level"] = "low"
            if result.get("confidence") not in ["high", "medium", "low"]:
                result["confidence"] = "low"
            if result.get("trend_direction") not in ["rising", "stable", "declining", "unknown"]:
                result["trend_direction"] = "unknown"
            
            return result
        except Exception as e:
            print(f"[demand_analyst] {model} failed: {e}")
    
    # Fallback if all models fail
    return {
        "level": "low",
        "data_sources_found": 0,
        "confidence": "low",
        "evidence": "Analysis failed - unable to process data",
        "trend_direction": "unknown",
        "requires_manual_research": True
    }


def _summarize_research(research_data: dict) -> tuple[str, int]:
    """
    Extract only meaningful fields from research data.
    Returns (summary_text, count_of_data_sources_found)
    Explicitly marks empty/irrelevant results so LLM knows what's missing.
    """
    summary = []
    sources_found = 0

    # GitHub
    github = research_data.get("github", {})
    if github.get("total_count", 0) > 0:
        sources_found += 1
        repos = github.get("top_repos", [])
        summary.append(f"✓ GITHUB: {github['total_count']} total repos found")
        for r in repos[:3]:
            stars = r.get('stars', 0)
            if stars > 0:
                summary.append(f"  - {r.get('name')} ({stars:,} stars)")
    else:
        summary.append("✗ GITHUB: 0 repositories found (no data for this topic)")

    # NPM
    npm = research_data.get("npm_trends", [])
    relevant_npm = [p for p in npm if p.get("downloads_last_month", 0) > 1000]
    if relevant_npm:
        sources_found += 1
        summary.append(f"✓ NPM: {len(relevant_npm)} packages with 1000+ downloads/month")
        for p in relevant_npm[:3]:
            summary.append(f"  - {p['name']}: {p['downloads_last_month']:,} downloads/month")
    else:
        summary.append("✗ NPM: No packages with significant downloads found")

    # Product Hunt
    ph = research_data.get("product_hunt", [])
    if ph and len(ph) > 0:
        sources_found += 1
        summary.append(f"✓ PRODUCT HUNT: {len(ph)} relevant products found")
        for p in ph[:3]:
            summary.append(f"  - {p.get('title','')[:80]}")
    else:
        summary.append("✗ PRODUCT HUNT: No relevant products found")

    # Tavily (Web Search)
    tavily = research_data.get("tavily", [])
    if tavily and len(tavily) > 0:
        sources_found += 1
        summary.append(f"✓ WEB SEARCH: {len(tavily)} results found")
        for t in tavily[:3]:
            summary.append(f"  - {t.get('title','')[:80]}")
    else:
        summary.append("✗ WEB SEARCH: No results found")

    # Google Trends
    gt = research_data.get("google_trends", {})
    if gt.get("direction") and gt["direction"] != "unknown":
        sources_found += 1
        peak = gt.get('peak_interest', 0)
        summary.append(f"✓ GOOGLE TRENDS: direction={gt['direction']}, peak_interest={peak}")
    else:
        summary.append("✗ GOOGLE TRENDS: No data or unknown direction")

    # Reddit
    reddit = research_data.get("reddit", [])
    if reddit and len(reddit) > 0:
        sources_found += 1
        summary.append(f"✓ REDDIT: {len(reddit)} discussions found")
    else:
        summary.append("✗ REDDIT: No discussions found")

    # News
    news = research_data.get("news", {})
    news_headlines = news.get("headlines", []) if isinstance(news, dict) else []
    if news_headlines and len(news_headlines) > 0:
        sources_found += 1
        summary.append(f"✓ NEWS: {len(news_headlines)} articles found")
    else:
        summary.append("✗ NEWS: No news articles found")

    # arXiv
    arxiv = research_data.get("arxiv", {})
    if arxiv.get("total_papers", 0) > 0:
        sources_found += 1
        summary.append(f"✓ ARXIV: {arxiv['total_papers']} academic papers found")
    else:
        summary.append("✗ ARXIV: No academic papers found")

    return "\n".join(summary), sources_found


def demand_analyst_node(state: IdeaValidationState) -> dict:
    summary, sources_found = _summarize_research(state.get("research_data", {}))
    prompt  = f"""
Idea: {state['idea']}
Idea Type: {state['idea_type']}
Data Sources Found: {sources_found} (out of 8 possible tools)

ACTUAL TOOL RESULTS (use ONLY these — do not add anything not listed):
{summary}

Based strictly on the above data:
1. If {sources_found} < 2, set confidence="low" and requires_manual_research=true
2. If most tools show 0 results, set level="low"
3. If you see real numbers and upward trends, you may set level="medium" or "high"
4. Never invent data not shown above
"""
    print(f"[demand_analyst] Analyzing demand ({sources_found} data sources found)...")
    result = call_llm(prompt)
    print(f"[demand_analyst] ✅ Done — level: {result.get('level')}, confidence: {result.get('confidence')}, trend: {result.get('trend_direction')}")
    return {"market_analysis": {"demand": result}}