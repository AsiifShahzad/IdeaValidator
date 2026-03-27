import os
import requests
from dotenv import load_dotenv
from backend.tools._keyword_extractor import extract_keyword_variants
load_dotenv()


def search_github(query: str) -> dict:
    try:
        headers  = {"Accept": "application/vnd.github+json"}
        token    = os.getenv("GITHUB_TOKEN", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        variants = extract_keyword_variants(query)
        url      = "https://api.github.com/search/repositories"

        for q in variants:
            print(f"[github] Trying: '{q}'")
            resp = requests.get(
                url, headers=headers,
                params={"q": q, "sort": "stars", "order": "desc", "per_page": 5},
                timeout=10
            )
            resp.raise_for_status()
            data  = resp.json()
            total = data.get("total_count", 0)

            if total > 0:
                repos = [{
                    "name":        r.get("full_name", ""),
                    "stars":       r.get("stargazers_count", 0),
                    "description": r.get("description", ""),
                    "url":         r.get("html_url", ""),
                } for r in data.get("items", [])]
                print(f"[github] ✅ Found {total} repos for '{q}'")
                return {"total_count": total, "top_repos": repos, "query_used": q}

        print("[github] All queries returned 0 results")
        return {"total_count": 0, "top_repos": [], "query_used": ""}

    except Exception as e:
        print(f"[github] Error: {e}")
        return {"total_count": 0, "top_repos": [], "query_used": ""}