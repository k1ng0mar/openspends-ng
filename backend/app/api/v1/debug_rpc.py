"""Debug endpoint to test RPC directly."""

from fastapi import APIRouter, HTTPException
import httpx
import logging
from app.core.config import settings
from app.services.embeddings import EmbeddingService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/debug-rpc")
async def debug_rpc():
    """Debug the vector search RPC."""
    # Test embedding generation
    svc = EmbeddingService(api_key=settings.OPENROUTER_API_KEY)
    query_emb = await svc.embed_single("healthcare hospital")
    dim = len(query_emb)
    
    # Check project count
    async with httpx.AsyncClient() as client:
        # Check projects with embeddings
        r = await client.get(
            f"{settings.SUPABASE_URL}/rest/v1/projects",
            headers={
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
            },
            params={"select": "id,title,embedding", "limit": 3}
        )
        projects = r.json()
        
        results = []
        for p in projects:
            emb = p.get("embedding")
            results.append({
                "id": p["id"],
                "title": p["title"][:30],
                "embedding_type": type(emb).__name__,
                "embedding_len": len(emb) if isinstance(emb, list) else None,
                "has_embedding": emb is not None
            })
        
        # Try RPC
        rpc_resp = await client.post(
            f"{settings.SUPABASE_URL}/rest/v1/rpc/match_projects",
            headers={
                "apikey": settings.SUPABASE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "query_embedding": query_emb,
                "match_threshold": 0.0,
                "match_count": 3
            }
        )
        
        return {
            "query_embedding_dim": dim,
            "first_three_values": query_emb[:3],
            "projects": results,
            "rpc_status": rpc_resp.status_code,
            "rpc_response": rpc_resp.text[:500] if rpc_resp.status_code != 200 else f"{len(rpc_resp.json())} results"
        }
