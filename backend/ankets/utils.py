import httpx
from fastapi import HTTPException
import json
from configs.settings import settings

AUTH_SERVICE_URL = f"http://{settings.AUTHENTIFICATION_SERVICE_HOST}:{settings.AUTHENTIFICATION_SERVICE_PORT}"
FRIENDS_SERVICE_URL = "http://localhost:8020"


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


async def get_id(cookie) -> int:
    if not await verify_auth(cookie):
        raise HTTPException(status_code=401, detail="Unauthorized")
    async with httpx.AsyncClient() as client:
        try:
            print("do reqeust")
            response = await client.post(
                f"{AUTH_SERVICE_URL}/get_user_id", cookies=cookie
            )
            print("done")
            response.raise_for_status()
            return response.json()["id"]
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, detail="User service error"
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail="Internal Server Error")


async def get_friends_list(cookie) -> int:
    if not await verify_auth(cookie):
        raise HTTPException(status_code=401, detail="Unauthorized")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{FRIENDS_SERVICE_URL}/friend_list", cookies=cookie
            )
            response.raise_for_status()
            return response.json()["friends"]
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, detail="User service error"
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail="Internal Server Error")
