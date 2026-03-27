"""
tavily_tool.py
--------------
General web search using Tavily API.
Returns top 5 results as list of dicts.
"""
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


def search_tavily(query: str) -> list[dict]:
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(query=query, max_results=5)

        results = []
        for r in response.get("results", []):
            results.append({
                "title":   r.get("title", ""),
                "url":     r.get("url", ""),
                "content": r.get("content", ""),
                "score":   r.get("score", 0),
            })
        return results

    except Exception as e:
        print(f"[tavily] Error: {e}")
        return []