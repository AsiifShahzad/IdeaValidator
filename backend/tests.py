"""
debug_tools.py
--------------
Tests exactly the tools each idea type would use.
Run from backend folder: python debug_tools.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from dotenv import load_dotenv
load_dotenv()

from backend.schemas.models import TOOLS_MAPPING
from backend.tools.tavily_tool        import search_tavily
from backend.tools.github_tool        import search_github
from backend.tools.google_trends_tool import get_google_trends
from backend.tools.reddit_tool        import search_reddit
from backend.tools.news_tool          import search_news
from backend.tools.product_hunt_tool  import search_product_hunt
from backend.tools.arxiv_tool         import search_arxiv

TOOL_REGISTRY = {
    "tavily":        search_tavily,
    "github":        search_github,
    "google_trends": get_google_trends,
    "reddit":        search_reddit,
    "news":          search_news,
    "product_hunt":  search_product_hunt,
    "arxiv":         search_arxiv,
}

# One test idea per idea type
TEST_CASES = {
    "dev_project":      "VS Code extension that auto-generates unit tests using AI",
    "business":         "Shopify duplicate product removal micro-SaaS tool",
    "research":         "Effect of CRISPR gene editing on antibiotic-resistant bacteria",
    "content":          "YouTube channel teaching AI tools to non-technical founders",
    "physical_product": "Autonomous delivery drone for last-mile logistics",
    "social_impact":    "NGO bringing digital literacy to rural school children",
}

import sys
# Allow running a specific type: python debug_tools.py dev_project
filter_type = sys.argv[1] if len(sys.argv) > 1 else None

for idea_type, idea in TEST_CASES.items():
    if filter_type and idea_type != filter_type:
        continue

    tools = TOOLS_MAPPING[idea_type]

    print("\n" + "=" * 65)
    print(f"  TYPE : {idea_type}")
    print(f"  IDEA : {idea}")
    print(f"  TOOLS: {tools}")
    print("=" * 65)

    for tool_name in tools:
        fn = TOOL_REGISTRY.get(tool_name)
        if not fn:
            print(f"\n── {tool_name.upper()} ── NOT IN REGISTRY")
            continue

        print(f"\n── {tool_name.upper()} ──────────────────────────────────────")
        try:
            result = fn(idea)
            if not result:
                print("  ⚠ Empty result returned")
            else:
                raw = json.dumps(result, indent=2)
                # Show first 600 chars so output stays readable
                print(raw[:600] + ("..." if len(raw) > 600 else ""))
        except Exception as e:
            print(f"  ❌ ERROR: {e}")

print("\n" + "=" * 65)
print("  Debug complete")
print("=" * 65)