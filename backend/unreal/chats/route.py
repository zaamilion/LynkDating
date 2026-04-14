from fastapi import APIRouter

from fastapi import HTTPException, status, Cookie, Request, Response
import utils
from models import *
from db.db_session import database_instance
import broker
import json

router = APIRouter()


@router.get("/get_chat")
async def get_chat(request: Request, user_id: int):
    current_user_id = await utils.get_self_id(request.cookies)
    chat_id = await database_instance.get_chat_id(current_user_id, user_id)
    if not chat_id:
        raise HTTPException(400, "Chat doesn't exists")
    chat_id = chat_id[0]["chat_id"]
    chat = await database_instance.get_chat(chat_id)
    if chat:
        return chat
    raise HTTPException(500)


@router.post("/send_message")
async def send_message(request: Request, message: Message):
    current_user_id = await utils.get_self_id(request.cookies)
    data = dict(message)
    data["sender_id"] = current_user_id
    data["cookie"] = request.cookies
    await broker.kafka_producer.send(topic="chat", value=json.dumps(data).encode())
    return {"status": "Message sent"}
