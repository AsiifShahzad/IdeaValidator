"""
pipeline.py
-----------
Full LangGraph pipeline.

Flow:
  classifier
      ↓
  research
      ↓
  [demand, competition, risk]  ← parallel via Send API
      ↓
  decision
      ↓
  reflection  (also builds final_output)
      ↓
  END
"""
from langgraph.graph import StateGraph, END
from langgraph.types import Send

from backend.schemas.models         import IdeaValidationState
from backend.agents.classifier      import classifier_node
from backend.agents.research        import research_node
from backend.agents.demand_analyst  import demand_analyst_node
from backend.agents.competition_analyst  import competition_analyst_node
from backend.agents.risk_analyst    import risk_analyst_node
from backend.agents.decision        import decision_node
from backend.agents.reflection      import reflection_node


def dispatch_analysts(state: IdeaValidationState) -> list[Send]:
    """Fan out to all 3 analysts in parallel after research."""
    return [
        Send("demand_analyst",      state),
        Send("competition_analyst", state),
        Send("risk_analyst",        state),
    ]


def build_graph():
    graph = StateGraph(IdeaValidationState)

    # Register all nodes
    graph.add_node("classifier",          classifier_node)
    graph.add_node("research",            research_node)
    graph.add_node("demand_analyst",      demand_analyst_node)
    graph.add_node("competition_analyst", competition_analyst_node)
    graph.add_node("risk_analyst",        risk_analyst_node)
    graph.add_node("decision",            decision_node)
    graph.add_node("reflection",          reflection_node)

    # Linear: classifier → research
    graph.set_entry_point("classifier")
    graph.add_edge("classifier", "research")

    # Fan out: research → 4 analysts in parallel
    graph.add_conditional_edges("research", dispatch_analysts)

    # Fan in: all analysts → decision
    graph.add_edge("demand_analyst",      "decision")
    graph.add_edge("competition_analyst", "decision")
    graph.add_edge("risk_analyst",        "decision")

    # Linear: decision → reflection → END
    graph.add_edge("decision",    "reflection")
    graph.add_edge("reflection",  END)

    return graph.compile()


pipeline = build_graph()