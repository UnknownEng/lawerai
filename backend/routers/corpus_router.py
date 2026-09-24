"""
Legal Knowledge Base Router
Direct statutory search, section viewer, and dynamic data-refresh mechanism.
"""

from fastapi import APIRouter, Query, HTTPException, status
from ..config import settings
from ingestion.vector_store import LegalVectorStore
from ingestion.corpus_loader import load_corpus_documents

router = APIRouter(prefix="/api/corpus", tags=["Legal Knowledge Base"])
vector_store = LegalVectorStore(storage_path=settings.VECTOR_STORE_PATH)


@router.get("/search")
async def search_corpus(
    q: str = Query(..., min_length=2, description="Search term, act name, or section number"),
    top_k: int = Query(5, ge=1, le=20),
    category: str = Query(None, description="Category filter"),
    jurisdiction: str = Query(None, description="Jurisdiction filter")
):
    results = vector_store.search_hybrid(
        query=q,
        top_k=top_k,
        category_filter=category,
        jurisdiction_filter=jurisdiction
    )
    return {
        "query": q,
        "count": len(results),
        "results": results
    }


@router.get("/section/{section_id}")
async def get_section_detail(section_id: str):
    """Retrieve full verbatim statutory text, procedural steps, and evidence for a specific section."""
    if not vector_store.documents:
        vector_store.load()

    target = section_id.upper()
    for doc in vector_store.documents:
        if doc.get("id", "").upper() == target:
            return doc

    raise HTTPException(status_code=404, detail=f"Statutory section '{section_id}' not found.")


@router.post("/refresh")
async def refresh_corpus():
    """
    Data-refresh mechanism: re-ingests and updates the legal corpus when laws are amended.
    """
    documents = load_corpus_documents(settings.CORPUS_DIR)
    if not documents:
        raise HTTPException(status_code=500, detail="Corpus directory is empty or unreadable.")

    vector_store.build_index(documents)
    return {
        "status": "success",
        "message": f"Successfully re-indexed {len(documents)} statutory sections.",
        "section_count": len(documents)
    }
