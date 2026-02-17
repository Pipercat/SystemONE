from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import redis

from app.core.config import settings

router = APIRouter(prefix="/api/peet", tags=["peet"])


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def peet_chat(payload: ChatRequest):
    """Simple PEET chat endpoint backed by Ollama, with graceful fallback."""
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL_CHAT,
                    "prompt": payload.message,
                    "stream": False,
                },
            )
        response.raise_for_status()
        data = response.json()
        return {"reply": data.get("response", "")}
    except Exception:
        return {"reply": "PEET ist aktuell beschäftigt. Bitte versuche es gleich erneut."}


@router.get("/system/healthcard")
async def peet_system_healthcard():
    """Aggregated health status for dashboard cards."""
    health = {"api": "online", "redis": "offline", "qdrant": "offline", "ollama": "offline"}

    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            socket_timeout=1,
        )
        if redis_client.ping():
            health["redis"] = "online"
    except Exception:
        pass

    try:
        async with httpx.AsyncClient(timeout=3) as client:
            qdrant = await client.get(f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/collections")
        if qdrant.status_code == 200:
            health["qdrant"] = "online"
    except Exception:
        pass

    try:
        async with httpx.AsyncClient(timeout=3) as client:
            ollama = await client.get(f"{settings.ollama_base_url}/api/tags")
        if ollama.status_code == 200:
            health["ollama"] = "online"
    except Exception:
        pass

    return health
