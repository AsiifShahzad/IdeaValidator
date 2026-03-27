"""
arxiv_tool.py
-------------
Uses arXiv API to search academic papers by keyword.
Returns paper count + top 3 titles.
"""
import requests
import xml.etree.ElementTree as ET


def search_arxiv(query: str) -> dict:
    try:
        url = "https://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start":        0,
            "max_results":  3,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        # arXiv returns XML — parse it
        root = ET.fromstring(response.text)
        ns   = {"atom": "http://www.w3.org/2005/Atom",
                "opensearch": "http://a9.com/-/spec/opensearch/1.1/"}

        total = root.find("opensearch:totalResults", ns)
        total_count = int(total.text) if total is not None else 0

        papers = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            link  = entry.find("atom:id", ns)
            papers.append({
                "title": title.text.strip() if title is not None else "",
                "url":   link.text.strip()  if link  is not None else "",
            })

        return {
            "total_papers": total_count,
            "top_papers":   papers,
        }

    except Exception as e:
        print(f"[arxiv] Error: {e}")
        return {"total_papers": 0, "top_papers": []}