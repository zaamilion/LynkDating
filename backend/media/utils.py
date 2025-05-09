import httpx
from configs.settings import settings
from fastapi import HTTPException

AUTH_SERVICE_URL = f"http://{settings.AUTHENTIFICATION_SERVICE_HOST}:{settings.AUTHENTIFICATION_SERVICE_PORT}"


async def get_self_id(cookie) -> int:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/get_user_id", cookies=cookie
            )
            response.raise_for_status()
            return response.json()["id"]
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, detail="User service error"
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail="Internal Server Error")
