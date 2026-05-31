"""MDA endpoints using Supabase REST API."""

from fastapi import APIRouter, Depends
from typing import List

from app.core.config import settings
from app.core.supabase_client import SupabaseClient

router = APIRouter()


def get_supabase() -> SupabaseClient:
    return SupabaseClient(
        url=settings.SUPABASE_URL,
        anon_key=settings.SUPABASE_KEY,
        service_key=settings.SUPABASE_SERVICE_KEY
    )


@router.get("/")
async def list_mdas(
    supabase: SupabaseClient = Depends(get_supabase)
):
    """List all MDAs."""
    return await supabase.get_mdas()


@router.get("/{mda_id}")
async def get_mda(
    mda_id: int,
    supabase: SupabaseClient = Depends(get_supabase)
):
    """Get a single MDA by ID."""
    mda = await supabase.get_mda(mda_id)
    if not mda:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="MDA not found")
    return mda
