"""Embedding service using OpenRouter's free Llama Nemotron embed model."""

import httpx
from typing import List, Optional


class EmbeddingService:
    """Generate embeddings via OpenRouter API."""
    
    def __init__(self, api_key: str, model: str = "openrouter/nvidia/llama-nemotron-embed-vl-1b-v2:free"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Returns a list of embedding vectors (each is a list of floats).
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "input": texts,
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # OpenRouter returns embeddings in data[i]['embedding']
            return [item["embedding"] for item in data["data"]]
    
    async def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = await self.embed([text])
        return embeddings[0]
