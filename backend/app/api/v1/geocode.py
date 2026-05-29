"""Geocoding endpoint — address to coordinates."""

from fastapi import APIRouter, HTTPException
from app.schemas import GeocodeRequest, GeocodeResponse

router = APIRouter()


@router.post("/", response_model=GeocodeResponse)
async def geocode_address(request: GeocodeRequest):
    """
    Geocode an address to lat/lng coordinates.
    Uses Nominatim (OpenStreetMap) as primary, with caching.
    """
    # TODO: implement Nominatim lookup + cache in geolocation_cache table
    raise HTTPException(status_code=501, detail="Geocoding not yet implemented")
