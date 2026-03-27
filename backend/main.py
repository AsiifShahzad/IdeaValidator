"""
main.py
-------
FastAPI app — REST + SSE streaming endpoints.
Run: uvicorn backend.main:app --reload  (from project root)
"""
import sys, os, time, json, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

# ── LangSmith Configuration ────────────────────────────────────────────────────
# If LANGSMITH_API_KEY is set, all traces will automatically be sent to LangSmith
# Set in .env: LANGSMITH_API_KEY, LANGSMITH_PROJECT, LANGSMITH_TRACING
import langsmith
if os.getenv("LANGSMITH_API_KEY"):
    print("✓ LangSmith tracing enabled")
    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault("LANGSMITH_PROJECT", "idea-validator")

from backend.graph.pipeline import pipeline
from backend.memory import get_history

app = FastAPI(title="Idea Validator API")

# ── CORS Configuration ─────────────────────────────────────────────────────────
# Only allow requests from trusted frontend URLs
allowed_origins = [
    "https://idea-validator-blue.vercel.app",  # Production frontend
    "http://localhost:5173",                     # Local Vite dev server
    "http://localhost:3000",                     # Alternative local dev port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup Event ─────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Log startup confirmation"""
    port = os.getenv("PORT", "8000")
    print(f"\n✅ Idea Validator API is running!")
    print(f"📊 Listening on http://0.0.0.0:{port}")
    print(f"📚 Docs available at http://0.0.0.0:{port}/docs\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown"""
    print("\n🛑 Idea Validator API shutting down...\n")


# ── Request/Response models ────────────────────────────────────────────────────

class IdeaRequest(BaseModel):
    idea: str


class ValidationResponse(BaseModel):
    idea:               str
    idea_type:          str
    tools_used:         list
    verdict:            str
    overall_score:      float
    confidence_percent: int
    success_factors:    list
    failure_reasons:    list
    similar_past_ideas: list
    reflection_notes:   str
    reasoning:          str
    demand:             dict
    competition:        dict
    risk:               dict
    # New user-facing fields
    demand_why:         str = ""
    competition_why:    str = ""
    risk_why:           str = ""
    next_steps:         list = []


# ── Initial state builder ──────────────────────────────────────────────────────

def make_initial_state(idea: str) -> dict:
    return {
        "idea":              idea,
        "idea_type":         "",
        "tools_assigned":    [],
        "tasks":             [],
        "research_data":     {},
        "market_analysis":   {},
        "business_analysis": {},
        "risk_analysis":     {},
        "decision":          {},
        "reflection":        "",
        "niche_suggestions": [],
        "final_output":      {},
    }


# ── POST /validate-idea ────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint — confirms API is running"""
    return {
        "name": "Idea Validator API",
        "version": "1.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "idea-validator"}


@app.post("/validate-idea", response_model=ValidationResponse)
async def validate_idea(request: IdeaRequest):
    """Run full pipeline and return final output."""
    if not request.idea.strip():
        raise HTTPException(status_code=400, detail="Idea cannot be empty")

    try:
        result = pipeline.invoke(make_initial_state(request.idea))
        final  = result.get("final_output", {})

        if not final:
            raise HTTPException(status_code=500, detail="Pipeline returned empty output")

        return ValidationResponse(**final)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /validate-idea/stream?idea=... — SSE streaming ────────────────────────

@app.get("/validate-idea/stream")
async def validate_idea_stream(idea: str):
    """
    Stream agent progress via Server-Sent Events.
    Each event: {agent, status, duration_ms}
    Frontend listens with EventSource API.
    """
    async def event_generator():
        state     = make_initial_state(idea)
        timings   = {}

        # We run each stage manually so we can emit SSE events between steps
        agents_in_order = [
            "classifier",
            "research",
            "demand_analyst",
            "competition_analyst",
            "risk_analyst",
            "decision",
            "reflection",
        ]

        # Emit "started" for all agents upfront
        for agent in agents_in_order:
            event = json.dumps({"agent": agent, "status": "pending", "duration_ms": 0})
            yield f"data: {event}\n\n"

        # Run pipeline — emit progress after each node using stream_mode
        try:
            for chunk in pipeline.stream(state, stream_mode="updates"):
                for node_name, node_output in chunk.items():
                    duration_ms = timings.get(node_name, 0)
                    event = json.dumps({
                        "agent":       node_name,
                        "status":      "complete",
                        "duration_ms": duration_ms,
                    })
                    yield f"data: {event}\n\n"
                    await asyncio.sleep(0)   # yield control to event loop

            # Final event with full result
            yield f"data: {json.dumps({'agent': 'pipeline', 'status': 'complete', 'duration_ms': 0})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'agent': 'pipeline', 'status': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── GET /history ───────────────────────────────────────────────────────────────

@app.get("/history")
async def get_validation_history(type: str = None):
    """
    Return past validations from Pinecone.
    Optional ?type=dev_project to filter by idea type.
    """
    try:
        history = get_history(idea_type=type)
        return {"count": len(history), "results": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))