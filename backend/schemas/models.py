from typing import TypedDict, List, Dict, Annotated


def merge_dicts(a: dict, b: dict) -> dict:
    return {**a, **b}


class IdeaValidationState(TypedDict):
    idea:               str
    idea_type:          str
    tools_assigned:     List[str]
    tasks:              List[str]
    research_data:      Dict
    market_analysis:    Annotated[Dict, merge_dicts]
    business_analysis:  Annotated[Dict, merge_dicts]
    risk_analysis:      Dict
    decision:           Dict
    reflection:         str
    niche_suggestions:  List[str]
    final_output:       Dict


IDEA_TYPES = [
    "business",
    "dev_project",
    "research",
    "content",
    "physical_product",
    "social_impact",
]

# Each idea type gets ONLY the tools that will return meaningful data for it
# arxiv        → only research (academic papers irrelevant for SaaS)
# google_trends → content/business/physical (trend data, not code metrics)
# github       → only dev_project (repos irrelevant for NGOs)
# news         → business/social_impact/physical (press coverage matters there)
# reddit       → all types (community discussion is always useful)
# product_hunt → dev_project/business/content (launches listed there)
# tavily       → all types (general web search always useful)

TOOLS_MAPPING = {
    "business": [
        "tavily",
        "google_trends",
        "news",
        "reddit",
        "product_hunt",
    ],
    "dev_project": [
        "github",
        "product_hunt",
        "tavily",
        "reddit",
    ],
    "research": [
        "arxiv",
        "tavily",
        "news",
        "reddit",
    ],
    "content": [
        "google_trends",
        "tavily",
        "reddit",
        "news",
    ],
    "physical_product": [
        "tavily",
        "google_trends",
        "news",
        "reddit",
    ],
    "social_impact": [
        "tavily",
        "news",
        "reddit",
        "google_trends",
    ],
}