import httpx
from fastapi import HTTPException
import json
from configs.settings import settings

AUTH_SERVICE_URL = f"http://{settings.AUTHENTIFICATION_SERVICE_HOST}:{settings.AUTHENTIFICATION_SERVICE_PORT}"
CHAT_SERVICE_URL = f"http://{settings.CHATS_SERVICE_HOST}:{settings.CHATS_SERVICE_PORT}"


async def verify_auth(cookie):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{AUTH_SERVICE_URL}/verify", cookies=cookie)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, detail="User service error"
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail="Internal Server Error")


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


async def send_message(cookie, user_id, message):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{CHAT_SERVICE_URL}/send_message",
                cookies=cookie,
                json={"user_id": user_id, "text": message},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise e
        except httpx.RequestError as e:
            print(e)
            raise HTTPException(status_code=503, detail="Internal Server Error")
