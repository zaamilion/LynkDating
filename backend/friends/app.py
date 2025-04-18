from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, Cookie, Request, Response
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
import utils
from models import *
from db import db
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()


@app.get("/friend_list")
async def get_friend_list(request: Request) -> FriendList:
    current_user_id = await utils.get_self_id(request.cookies)
    friends_list = db.get_friends_list(current_user_id)
    return FriendList(friends=friends_list)


@app.get("/friend_requests_receiver_list")
async def get_friend_requests_receiver_list(request: Request) -> FriendRequestsList:
    current_user_id = await utils.get_self_id(request.cookies)
    requests_list = db.get_friend_receiver_requests_list(current_user_id)
    return FriendRequestsList(requests=requests_list)


@app.get("/friend_requests_sender_list")
async def get_friend_requests_sender_list(request: Request) -> FriendRequestsList:
    current_user_id = await utils.get_self_id(request.cookies)
    requests_list = db.get_friend_sender_requests_list(current_user_id)
    return FriendRequestsList(requests=requests_list)


@app.post("/send_friend_request")
async def send_friend_request(request: Request, user_id: int) -> dict:
    current_user_id = await utils.get_self_id(request.cookies)
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't send friend request to yourself",
        )
    result = db.send_friend_request(current_user_id, user_id)
    if result:
        # notification service need to send notification to receiver of request
        return {"message": "Succesfully sended"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry....",
        )


@app.post("/cancel_friend_request")
async def cancel_friend_request(request: Request, user_id: int) -> dict:
    current_user_id = await utils.get_self_id(request.cookies)
    result = db.cancel_friend_request(current_user_id, user_id)
    if result:
        return {"message": "Succesfully canceled"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry....",
        )


@app.post("/accept_friend_request")
async def accept_friend_request(request: Request, user_id: int) -> dict:
    current_user_id = await utils.get_self_id(request.cookies)
    result = db.accept_friend_request(user_id, current_user_id)
    if result:
        return {"message": "Succesfully accepted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry....",
        )


@app.post("/decline_friend_request")
async def decline_friend_request(request: Request, user_id: int) -> dict:
    current_user_id = await utils.get_self_id(request.cookies)
    result = db.decline_friend_request(user_id, current_user_id)
    if result:
        return {"message": "Succesfully declined"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry....",
        )


@app.post("/delete_friend")
async def decline_friend_request(request: Request, user_id: int) -> dict:
    current_user_id = await utils.get_self_id(request.cookies)
    result = db.delete_friend(user_id, current_user_id)
    if result:
        return {"message": "Succesfully deleted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry....",
        )
