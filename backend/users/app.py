from fastapi import FastAPI

from db.db_session import database_instance

app = FastAPI()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import route
from db.db_session import database_instance

app = FastAPI()

# убрать нахуй после тестирования
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database_instance.connect()


app.include_router(route.router)
