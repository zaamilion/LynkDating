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
        answer = await client.post(
            f"http://localhost:8080/upload",
            cookies=cookie,
            files={"file": open(filename, "rb")},
        )
        answer.raise_for_status()
        return answer.json()


import asyncio
import time

start = time.time()
filename = input("Введите название файла:")
print(asyncio.run(main(filename)))

end = time.time() - start

print(end)
