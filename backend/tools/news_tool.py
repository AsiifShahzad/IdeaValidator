import os
import requests
from dotenv import load_dotenv
from backend.tools._keyword_extractor import extract_keyword_variants
load_dotenv()

NEGATIVE_WORDS = {"fail","crash","loss","decline","ban","risk","danger","problem","lawsuit","fraud"}
POSITIVE_WORDS = {"growth","success","launch","raise","profit","win","expand","innovation","funding"}


def _sentiment(text: str) -> str:
    t   = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in t)
    neg = sum(1 for w in NEGATIVE_WORDS if w in t)
    return "positive" if pos > neg else "negative" if neg > pos else "neutral"


def search_news(query: str) -> dict:
    try:
        api_key  = os.getenv("NEWS_API_KEY", "")
        variants = extract_keyword_variants(query)

        for q in variants:
            print(f"[news] Trying: '{q}'")
            resp = requests.get(
                "https://newsapi.org/v2/everything",
                params={"q": q, "pageSize": 5, "sortBy": "relevancy", "apiKey": api_key},
                timeout=10
            )
            resp.raise_for_status()
            articles = resp.json().get("articles", [])

            if not articles:
                continue

            headlines = [{
                "title":     a.get("title", ""),
                "url":       a.get("url", ""),
                "sentiment": _sentiment(a.get("title", "")),
            } for a in articles if a.get("title")]

            if headlines:
                overall = _sentiment(" ".join(h["title"] for h in headlines))
                print(f"[news] ✅ Found {len(headlines)} headlines for '{q}'")
                return {"headlines": headlines, "overall_sentiment": overall}

        print("[news] No headlines found")
        return {"headlines": [], "overall_sentiment": "neutral"}

    except Exception as e:
        print(f"[news] Error: {e}")
        return {"headlines": [], "overall_sentiment": "neutral"}