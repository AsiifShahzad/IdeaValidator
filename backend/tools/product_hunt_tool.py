"""
product_hunt_tool.py
--------------------
Uses Tavily with a tighter site:producthunt.com query.
Filters out results that don't mention keywords from the query.
"""
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


def search_product_hunt(query: str) -> list[dict]:
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        # Use quotes around key terms for tighter matching
        keywords = [w for w in query.split() if len(w) > 3]
        tight_query = f'site:producthunt.com {" ".join(keywords[:4])}'

        response = client.search(query=tight_query, max_results=5)

        # Filter: only keep results where at least one keyword appears in title or content
        products = []
        for r in response.get("results", []):
            title   = r.get("title", "").lower()
            content = r.get("content", "").lower()
            combined = title + " " + content

            relevance = sum(1 for w in keywords if w.lower() in combined)
            if relevance < 1:
                continue

            products.append({
                "title":       r.get("title", ""),
                "url":         r.get("url", ""),
                "description": r.get("content", "")[:300],
            })

        return products

    except Exception as e:
        print(f"[product_hunt] Error: {e}")
        return []