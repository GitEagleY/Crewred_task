import httpx


async def validate_artwork(artwork_id: str) -> dict | None:
    """Validate artwork exists in Art Institute API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.artic.edu/api/v1/artworks/{artwork_id}",
                timeout=5
            )
        if response.status_code == 200:
            data = response.json().get("data")
            return {
                "id": str(data.get("id")),
                "title": data.get("title", ""),
                "url": data.get("url"),
            }
        return None
    except Exception:
        return None