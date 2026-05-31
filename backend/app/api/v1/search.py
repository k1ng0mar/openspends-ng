"""Semantic search endpoints using vector embeddings."""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
import httpx

from app.core.config import settings
from app.core.supabase_client import SupabaseClient
from app.services.embeddings import EmbeddingService

router = APIRouter()


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
    supabase: SupabaseClient = Depends(get_supabase),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    """Generate and store embeddings for all projects without embeddings.
    
    Uses Llama Nemotron via OpenRouter (free).
    """
    # Fetch projects without embeddings
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.SUPABASE_URL}/rest/v1/projects",
            headers={
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
            },
            params={
                "select": "id,title,contractor,source",
                "embedding": "is.null"
            }
        )
        projects = response.json()
    
    if not projects:
        return {"message": "All projects already have embeddings", "embedded": 0}
    
    # Build text to embed (title + contractor + metadata)
    texts = []
    for p in projects:
        text = p["title"]
        if p.get("contractor"):
            text += f" by {p['contractor']}"
        texts.append(text)
    
    # Generate embeddings
    embeddings = await embedding_service.embed(texts)
    
    # Update projects with embeddings
    updated = 0
    async with httpx.AsyncClient() as client:
        for p, emb in zip(projects, embeddings):
            # Format as Postgres vector string
            vector_str = "[" + ",".join(str(x) for x in emb) + "]"
            
            await client.patch(
                f"{settings.SUPABASE_URL}/rest/v1/projects?id=eq.{p['id']}",
                headers={
                    "apikey": settings.SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                json={"embedding": vector_str}
            )
            updated += 1
    
    return {"message": f"Embedded {updated} projects", "embedded": updated}


@router.get("/semantic")
async def semantic_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    supabase: SupabaseClient = Depends(get_supabase),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    """Semantic search over projects using vector similarity.
    
    Returns projects most semantically similar to the query.
    
    Example queries:
    - "road construction in the north"
    - "healthcare spending"
    - "power plant hydroelectric"
    """
    # Generate embedding for query
    query_embedding = await embedding_service.embed_single(q)
    vector_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    
    # Use Supabase RPC for vector search
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.SUPABASE_URL}/rest/v1/rpc/match_projects",
            headers={
                "apikey": settings.SUPABASE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "query_embedding": vector_str,
                "match_threshold": 0.5,
                "match_count": limit
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Search failed")
        
        results = response.json()
    
    return {
        "query": q,
        "results": results
    }
