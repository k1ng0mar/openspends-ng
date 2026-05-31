"""States endpoints using Supabase REST API."""

from fastapi import APIRouter, Depends
from typing import List, Optional

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
async def list_states(
    supabase: SupabaseClient = Depends(get_supabase)
):
    """List all states."""
    return await supabase.get_states()
