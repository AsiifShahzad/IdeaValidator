"""
_keyword_extractor.py
---------------------
Two-tier keyword extraction:
1. LLM-based (primary) — uses Groq to extract smart keywords from complex ideas
2. Rule-based (fallback) — kicks in if LLM fails or is too slow

Used by: google_trends, news, github tools.
"""
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

# ── Rule-based fallback data ───────────────────────────────────────────────────

STOP_WORDS = {
    "a","an","the","for","and","or","of","to","in","is","are","was","were",
    "that","this","with","using","based","about","from","into","onto","upon",
    "build","create","make","want","help","helps","teach","teaches","teaching",
    "bring","brings","bringing","launch","launching","start","starting",
    "focused","designed","targeted","aimed","called","named","provide","provides",
    "working","building","getting","trying","helping","allowing","enabling",
    "i","we","you","they","their","your","our","its","my","his","her",
    "which","who","what","when","how","where","why","can","will","should",
    "just","only","also","more","most","very","really","quite","like",
    "better","best","good","great","new","simple","easy","fast","quick",
    "youtube","channel","newsletter","podcast","blog","website","platform",
    "startup","business","company","tool","app","saas","micro","software",
    "solution","service","system","product","project","idea","concept",
    "non","technical","nontechnical",
}

KEEP_SHORT = {
    "ai","ml","vr","ar","iot","api","sdk","ui","ux","hr","crm","erp",
    "b2b","b2c","ngo","ngos","ceo","cto","seo","llm","gpt",
}

HIGH_VALUE = {
    "crispr","blockchain","drone","drones","shopify","github","vscode",
    "react","python","javascript","typescript","rust","golang","kubernetes",
    "docker","tensorflow","pytorch","openai","climate","cancer","diabetes",
    "ecommerce","fintech","healthtech","edtech","proptech","legaltech",
    "automation","robotics","autonomous","electric","solar","biotech",
    "cybersecurity","quantum","satellite","genetic","neural",
}


def _rule_based(idea: str, max_words: int = 3) -> list[str]:
    """Fast rule-based extraction — no API call needed."""
    words  = idea.lower().replace(",","").replace("-"," ").replace("/"," ").split()
    scored = []

    for word in words:
        clean = word.strip(".,!?;:()'\"")
        if not clean:
            continue
        if clean in HIGH_VALUE:
            scored.append((3, clean))
        elif clean in KEEP_SHORT:
            scored.append((2, clean))
        elif clean in STOP_WORDS or len(clean) <= 3:
            continue
        else:
            scored.append((1, clean))

    scored.sort(key=lambda x: -x[0])
    seen, unique = set(), []
    for _, w in scored:
        if w not in seen:
            seen.add(w)
            unique.append(w)

    return unique[:max_words]


def _llm_based(idea: str) -> str | None:
    """
    Uses Groq llama-3.1-8b-instant to extract smart search keywords.
    Returns None on failure so caller can fall back to rule-based.
    """
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # fast + cheap for this task
            messages=[{
                "role": "system",
                "content": (
                    "You extract search keywords from startup idea descriptions. "
                    "Return ONLY 2-3 keywords that best represent the core topic. "
                    "No explanation, no punctuation, just the keywords. "
                    "Examples:\n"
                    "Idea: 'YouTube channel teaching AI tools to non-technical founders' → 'AI tools founders'\n"
                    "Idea: 'NGO bringing digital literacy to rural school children' → 'digital literacy rural'\n"
                    "Idea: 'Shopify duplicate product removal micro-SaaS' → 'shopify duplicate removal'\n"
                    "Idea: 'CRISPR gene editing on antibiotic-resistant bacteria' → 'CRISPR antibiotic resistance'\n"
                )
            }, {
                "role": "user",
                "content": f"Idea: {idea}"
            }],
            temperature=0,
            max_tokens=20,   # keywords only — very short
        )
        keywords = response.choices[0].message.content.strip()

        # Sanity check — reject if too long or looks like a sentence
        if len(keywords) > 60 or len(keywords.split()) > 5:
            return None

        return keywords

    except Exception as e:
        print(f"[extractor] LLM failed: {e}")
        return None


def extract_keywords(idea: str) -> str:
    """
    Primary entry point — tries LLM first, falls back to rule-based.
    Returns a single best keyword string.
    """
    llm_result = _llm_based(idea)
    if llm_result:
        print(f"[extractor] LLM keywords: '{llm_result}'")
        return llm_result

    rule_result = " ".join(_rule_based(idea, max_words=2))
    print(f"[extractor] Rule-based fallback: '{rule_result}'")
    return rule_result


def extract_keyword_variants(idea: str) -> list[str]:
    """
    Returns a ranked fallback chain of queries: 3-word → 2-word → 1-word.
    Used by tools that retry with progressively simpler queries.
    """
    # Try LLM for the primary query
    llm_result = _llm_based(idea)

    rule_words = _rule_based(idea, max_words=3)

    variants = []
    if llm_result:
        variants.append(llm_result)                          # LLM result first

    if len(rule_words) >= 3:
        variants.append(" ".join(rule_words[:3]))
    if len(rule_words) >= 2:
        variants.append(" ".join(rule_words[:2]))
    if rule_words:
        variants.append(rule_words[0])

    # Deduplicate while preserving order
    seen, unique = set(), []
    for v in variants:
        if v not in seen:
            seen.add(v)
            unique.append(v)

    return unique if unique else [idea[:20]]