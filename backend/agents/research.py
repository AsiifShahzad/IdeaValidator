"""
research.py — LangGraph node
Runs only the tools in state.tools_assigned — nothing else.
Each idea type gets a different tool set from TOOLS_MAPPING.
"""
import asyncio
import nest_asyncio
from backend.schemas.models import IdeaValidationState

from backend.tools.tavily_tool        import search_tavily
from backend.tools.github_tool        import search_github
from backend.tools.google_trends_tool import get_google_trends
from backend.tools.reddit_tool        import search_reddit
from backend.tools.news_tool          import search_news
from backend.tools.product_hunt_tool  import search_product_hunt
from backend.tools.arxiv_tool         import search_arxiv

nest_asyncio.apply()

# Only tools listed here can ever be called
# Adding a tool to TOOLS_MAPPING but not here = safe no-op (logs warning)
TOOL_REGISTRY = {
    "tavily":        search_tavily,
    "github":        search_github,
    "google_trends": get_google_trends,
    "reddit":        search_reddit,
    "news":          search_news,
    "product_hunt":  search_product_hunt,
    "arxiv":         search_arxiv,
}


async def run_tool(tool_name: str, idea: str) -> tuple[str, any]:
    fn = TOOL_REGISTRY.get(tool_name)
    if fn is None:
        print(f"[research] ⚠ Unknown tool '{tool_name}' — skipping")
        return tool_name, {}
    try:
        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, fn, idea)
        # Treat empty results explicitly
        if not result:
            print(f"[research] ⚠ {tool_name} returned empty")
            return tool_name, {}
        print(f"[research] ✅ {tool_name} done")
        return tool_name, result
    except Exception as e:
        print(f"[research] ❌ {tool_name} failed: {e}")
        return tool_name, {}


async def run_all_tools(tools: list[str], idea: str) -> dict:
    tasks   = [run_tool(tool, idea) for tool in tools]
    results = await asyncio.gather(*tasks)
    return {name: data for name, data in results}


def research_node(state: IdeaValidationState) -> dict:
    tools = state["tools_assigned"]
    print(f"\n[research] idea_type={state['idea_type']} → running tools: {tools}")

    loop          = asyncio.get_event_loop()
    research_data = loop.run_until_complete(run_all_tools(tools, state["idea"]))

    # Log what came back vs what was empty
    for tool in tools:
        data = research_data.get(tool)
        if not data:
            print(f"[research] ⚠ {tool}: no data returned")

    return {"research_data": research_data}