"""Semantic search endpoints using vector embeddings."""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
import httpx
import logging

from app.core.config import settings
from app.core.supabase_client import SupabaseClient
from app.services.embeddings import EmbeddingService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_supabase() -> SupabaseClient:
    return SupabaseClient(
        url=settings.SUPABASE_URL,
        anon_key=settings.SUPABASE_KEY,
        service_key=settings.SUPABASE_SERVICE_KEY
    )


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(api_key=settings.OPENROUTER_API_KEY)


@router.post("/embed")
async def embed_projects(
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    """Generate and store embeddings for all projects without embeddings.
    
    Uses Llama Nemotron via OpenRouter (free).
    """
    if not settings.OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")
    
    # Fetch all projects
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{settings.SUPABASE_URL}/rest/v1/projects",
            headers={
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
            },
            params={"select": "id,title,contractor,embedding"}
        )
        response.raise_for_status()
        projects = response.json()
    
    # Filter projects without embeddings
    projects_to_embed = [p for p in projects if p.get("embedding") is None]
    
    if not projects_to_embed:
        return {"message": "All projects already have embeddings", "embedded": 0}
    
    logger.info(f"Embedding {len(projects_to_embed)} projects...")
    
    # Build text to embed (title + contractor + metadata)
    texts = []
    for p in projects_to_embed:
        text = p["title"]
        if p.get("contractor"):
            text += f" by {p['contractor']}"
        texts.append(text)
    
    try:
        # Generate embeddings
        embeddings = await embedding_service.embed(texts)
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")
    
    # Update projects with embeddings
    updated = 0
    async with httpx.AsyncClient(timeout=30.0) as client:
        for p, emb in zip(projects_to_embed, embeddings):
            await client.patch(
                f"{settings.SUPABASE_URL}/rest/v1/projects?id=eq.{p['id']}",
                headers={
                    "apikey": settings.SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                json={"embedding": emb}  # pass list directly, not string
            )
            updated += 1
    
    return {"message": f"Embedded {updated} projects", "embedded": updated}


@router.get("/semantic")
async def semantic_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    """Semantic search over projects using vector similarity.
    
    Returns projects most semantically similar to the query.
    
    Example queries:
    - "road construction in the north"
    - "healthcare spending"
    - "power plant hydroelectric"
    """
    if not settings.OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")
    
    try:
        # Generate embedding for query
        query_embedding = await embedding_service.embed_single(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")
    
    # Use Supabase RPC for vector search
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.SUPABASE_URL}/rest/v1/rpc/match_projects",
            headers={
                "apikey": settings.SUPABASE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "query_embedding": query_embedding,  # pass as list, not string
                "match_threshold": 0.15,
                "match_count": limit
            }
        )
        
        if response.status_code != 200:
            logger.error(f"RPC failed: {response.text}")
            raise HTTPException(status_code=500, detail=f"Search failed: {response.text}")
        
        results = response.json()
    
    return {
        "query": q,
        "count": len(results),
        "results": results
    }
