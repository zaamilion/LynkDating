from fastapi import APIRouter

from fastapi import HTTPException, status, Cookie, Request, Response
import utils
from models import *
from db.db_session import database_instance
from configs.settings import settings
import json
import broker

router = APIRouter()


@router.get("/get_balance")
async def get_balance(request: Request):
    current_user_id = await utils.get_self_id(request.cookies)
    balance = await database_instance.get_balance(current_user_id)
    if not balance:
        raise HTTPException(500)


@router.get("/generate_payment_link")
async def generate_payment_link(request: Request, amount: int):
    current_user_id = await utils.get_self_id(request.cookies)
    data = {"user_id": current_user_id, "amount": amount}
    payload = json.dumps(data)
    link = settings.PAYMENT_BOT_LINK + payload
    return {"link": link}


# pupupupupu
@router.post("/buy_gift")
async def buy_gift(request: Request, gift_id: int):
    current_user_id = await utils.get_self_id(request.cookies)
    balance = await database_instance.get_balance(current_user_id)
    gift = await database_instance.get_gift(gift_id)
    if not gift:
        raise HTTPException(400, "Gift doesn't exists")
    if gift["price"] > balance:
        raise HTTPException(402, "Insufficient funds")
    await database_instance.buy_gift(gift, current_user_id)
    return {"status": "sucessfully buyed"}


@router.post("/send_gift")
async def send_gift(request: Request, gift_id: int, user_id: int):
    current_user_id = await utils.get_self_id(request.cookies)
    balance = await database_instance.get_balance(current_user_id)
    gift = await database_instance.get_gift(gift_id)
    if not gift:
        raise HTTPException(400, "Gift doesn't exists")
    if gift["price"] > balance:
        raise HTTPException(402, "Insufficient funds")
    await database_instance.buy_gift(gift, current_user_id, user_id)
    await utils.send_message(request.cookies, user_id, json.dumps(dict(gift)))
    return {"status": "sucessfully sended"}


@router.post("/sell_gift")
async def sell_gift(request: Request, gift_id: int):
    current_user_id = await utils.get_self_id(request.cookies)
    user_gift = await database_instance.get_user_gift(gift_id)
    if user_gift["owner_id"] != current_user_id:
        raise HTTPException(403, "It's not your gift")
    if not user_gift:
        raise HTTPException(400, "Gift doesn't exists")
    if user_gift["sold"]:
        raise HTTPException(400, "Gift already sold")
    await database_instance.sell_gift(user_gift)


"""    current_user_id = await utils.get_self_id(request.cookies)
    data = dict(message)
    data["sender_id"] = current_user_id
    data["cookie"] = request.cookies
    await broker.kafka_producer.send(topic="chat", value=json.dumps(data).encode())
    return {"status": "Message sent"}
"""
