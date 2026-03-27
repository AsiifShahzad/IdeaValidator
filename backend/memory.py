"""
memory.py
---------
Pinecone vector memory for storing and retrieving past idea validations.
Filters by idea_type so dev projects never compare to business ideas.
"""
import os
import json
import hashlib
from dotenv import load_dotenv
load_dotenv()

from pinecone import Pinecone, ServerlessSpec
from groq import Groq

PINECONE_API_KEY  = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX    = os.getenv("PINECONE_INDEX", "idea-validator")
EMBEDDING_MODEL   = "llama-3.1-8b-instant"   # used to generate embeddings via Groq

_pc    = None
_index = None


def _get_index():
    """Lazy init — only connects when first needed."""
    global _pc, _index
    if _index is not None:
        return _index

    if not PINECONE_API_KEY:
        print("[memory] No PINECONE_API_KEY set — memory disabled")
        return None

    try:
        _pc = Pinecone(api_key=PINECONE_API_KEY)

        # Create index if it doesn't exist
        existing = [i.name for i in _pc.list_indexes()]
        if PINECONE_INDEX not in existing:
            _pc.create_index(
                name=PINECONE_INDEX,
                dimension=3072,          # llama3 embedding size via Groq
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            print(f"[memory] Created Pinecone index: {PINECONE_INDEX}")

        _index = _pc.Index(PINECONE_INDEX)
        print(f"[memory] Connected to Pinecone index: {PINECONE_INDEX}")
        return _index

    except Exception as e:
        print(f"[memory] Pinecone init failed: {e}")
        return None


def _get_embedding(text: str) -> list[float]:
    """
    Get text embedding using Groq.
    NOTE: Groq doesn't have a dedicated embedding model yet.
    For now, using a simple hash-based similarity approach instead.
    """
    try:
        # Groq doesn't have embeddings API yet - would need to use LangChain
        # Fall back to returning empty embedding to skip this feature
        return []
    except Exception as e:
        print(f"[memory] Embedding failed: {e}")
        return []


def _make_id(idea: str) -> str:
    """Stable ID from idea text."""
    return hashlib.md5(idea.encode()).hexdigest()


def store_validation(final_output: dict) -> bool:
    """
    Store a completed validation in Pinecone.
    Includes idea_type in metadata for filtered search.
    """
    index = _get_index()
    if index is None:
        return False

    try:
        idea      = final_output.get("idea", "")
        idea_type = final_output.get("idea_type", "")
        verdict   = final_output.get("verdict", "")
        score     = final_output.get("overall_score", 0)

        embedding = _get_embedding(idea)
        if not embedding:
            return False

        # Store compact summary in metadata (Pinecone has 40KB metadata limit)
        metadata = {
            "idea":        idea[:500],
            "idea_type":   idea_type,
            "verdict":     verdict,
            "score":       float(score),
            "confidence":  float(final_output.get("confidence_percent", 0)),
            "success_factors": json.dumps(final_output.get("success_factors", [])[:3]),
            "failure_reasons": json.dumps(final_output.get("failure_reasons", [])[:2]),
            "reasoning":   str(final_output.get("reasoning", ""))[:500],
        }

        index.upsert(vectors=[{
            "id":       _make_id(idea),
            "values":   embedding,
            "metadata": metadata,
        }])

        print(f"[memory] ✅ Stored validation for: {idea[:60]}")
        return True

    except Exception as e:
        print(f"[memory] Store failed: {e}")
        return False


def search_similar_ideas(idea: str, idea_type: str, top_k: int = 3) -> list[dict]:
    """
    Search Pinecone for similar past validations.
    Filters by idea_type — dev projects only compare to dev projects.
    """
    index = _get_index()
    if index is None:
        return []

    try:
        embedding = _get_embedding(idea)
        if not embedding:
            return []

        results = index.query(
            vector=embedding,
            top_k=top_k,
            filter={"idea_type": {"$eq": idea_type}},   # type-aware filter
            include_metadata=True,
        )

        similar = []
        for match in results.get("matches", []):
            meta = match.get("metadata", {})
            similar.append({
                "idea":            meta.get("idea", ""),
                "verdict":         meta.get("verdict", ""),
                "score":           meta.get("score", 0),
                "success_factors": json.loads(meta.get("success_factors", "[]")),
                "failure_reasons": json.loads(meta.get("failure_reasons", "[]")),
                "similarity":      round(match.get("score", 0), 3),
            })

        print(f"[memory] Found {len(similar)} similar {idea_type} ideas")
        return similar

    except Exception as e:
        print(f"[memory] Search failed: {e}")
        return []

def get_history(idea_type: str = None, limit: int = 20) -> list[dict]:
    """
    Fetch stored validations, optionally filtered by idea_type.
    Used by GET /history endpoint.
    """
    index = _get_index()
    if index is None:
        return []

    try:
        # Pinecone doesn't support list/scan directly — use a broad query
        # with a zero vector and metadata filter
        dummy_vector = [0.0] * 3072
        filter_query = {"idea_type": {"$eq": idea_type}} if idea_type else {}

        results = index.query(
            vector=dummy_vector,
            top_k=limit,
            filter=filter_query,
            include_metadata=True,
        )

        history = []
        for match in results.get("matches", []):
            meta = match.get("metadata", {})
            history.append({
                "idea":      meta.get("idea", ""),
                "idea_type": meta.get("idea_type", ""),
                "verdict":   meta.get("verdict", ""),
                "score":     meta.get("score", 0),
            })

        return history

    except Exception as e:
        print(f"[memory] History fetch failed: {e}")
        return []                                                                                            