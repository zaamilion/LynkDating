from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, Cookie, Request, Response
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
import utils
import asyncio
from models import *
from dotenv import load_dotenv
from db.db_session import database_instance
from route import router
import chats.broker as broker

load_dotenv()

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
async def start():
    await broker.kafka_producer.start()
    asyncio.create_task(broker.start_kafka_consumer())
