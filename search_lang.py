import os
import httpx
from typing import Dict, List

async def search_web(query: str) -> List[Dict]:
    api_key = os.getenv("SERP_API_KEY", "")
    if not api_key:
        return [{"title": "Error", "snippet": "SERP_API_KEY missing", "url": ""}]

    params = {
        "q": query,
        "api_key": api_key,
        "num": 6,
        "engine": "google",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get("https://serpapi.com/search", params=params, timeout=30.0)
        data = response.json()
        results = []

        for item in data.get("organic_results", []):
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
            })

    return results
