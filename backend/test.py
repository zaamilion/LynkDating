import httpx
import random


async def main(filename):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"http://localhost:8000/signin",
                data={"username": "bombardiro", "password": "crocodilo"},
            )
            response.raise_for_status()
            cookie = response.cookies
        except Exception as e:
            raise e
    tasks = []
    async with httpx.AsyncClient() as client:
        answer = await client.get(
            f"http://localhost:3000/me",
            cookies=cookie,
        )
        answer.raise_for_status()
        return answer.text


import asyncio
import time

start = time.time()
filename = input("Введите название файла:")
print(asyncio.run(main(filename)))

end = time.time() - start

print(end)
