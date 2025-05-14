from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, Cookie, Request, Response
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from fastapi.middleware.cors import CORSMiddleware
import utils
from models import *
from dotenv import load_dotenv
from db.db_session import database_instance
from route import router
import asyncio
import broker

load_dotenv()
"http://localhost:3000"
app = FastAPI()
origins = [
    "http://localhost:3000",  # Замени на адрес твоего фронтенда
]

# убрать нахуй после тестирования
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.on_event("startup")
async def start():
    await broker.kafka_producer.start()
    asyncio.create_task(broker.start_kafka_consumer())
