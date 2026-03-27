"""
reddit_tool.py
--------------
Finds relevant Reddit threads using Tavily with site:reddit.com filter.
"""
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


def search_reddit(query: str) -> list[dict]:
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(
            query=f"site:reddit.com {query}",
            max_results=5
        )

        threads = []
        for r in response.get("results", []):
            threads.append({
                "title":   r.get("title", ""),
                "url":     r.get("url", ""),
                "snippet": r.get("content", "")[:300],
            })
        return threads

    except Exception as e:
        print(f"[reddit] Error: {e}")
        return []