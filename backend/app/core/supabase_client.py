"""Supabase REST API client for database operations."""

import httpx
from typing import Optional, List, Dict, Any


class SupabaseClient:
    """Client for Supabase REST API operations."""
    
    def __init__(self, url: str, anon_key: str, service_key: str):
        self.url = url.rstrip("/")
        self.anon_key = anon_key
        self.service_key = service_key
        
    def _headers(self, use_service: bool = False) -> dict:
        key = self.service_key if use_service else self.anon_key
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
    
    async def get_projects(
        self,
        state_id: Optional[int] = None,
        status: Optional[str] = None,
        mda_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Fetch projects from Supabase REST API."""
        params = {
            "select": "id,title,mda_id,state_id,lga_id,contractor,start_date,end_date,status,budget_allocated,spent,latitude,longitude,source,embedding",
            "limit": limit,
            "offset": offset
        }
        
        if state_id:
            params["state_id"] = f"eq.{state_id}"
        if status:
            params["status"] = f"eq.{status}"
        if mda_id:
            params["mda_id"] = f"eq.{mda_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.url}/rest/v1/projects",
                headers=self._headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single project by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.url}/rest/v1/projects",
                headers=self._headers(),
                params={"id": f"eq.{project_id}", "select": "*"}
            )
            response.raise_for_status()
            data = response.json()
            return data[0] if data else None
    
    async def get_mdas(self) -> List[Dict[str, Any]]:
        """Fetch all MDAs."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.url}/rest/v1/mdas",
                headers=self._headers(),
                params={"select": "id,name,code,level"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_states(self) -> List[Dict[str, Any]]:
        """Fetch all states."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.url}/rest/v1/states",
                headers=self._headers(),
                params={"select": "id,name,region"}
            )
            response.raise_for_status()
            return response.json()
    
    async def count_projects(self) -> int:
        """Get total project count."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.url}/rest/v1/projects",
                headers=self._headers(),
                params={"select": "count"}
            )
            response.raise_for_status()
            data = response.json()
            return data[0]["count"] if data else 0
