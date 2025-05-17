from fastapi import APIRouter

from fastapi import HTTPException, status, Cookie, Request, Response
import utils
from models import *
from db.db_session import database_instance
import broker
import json
from broker import kafka_producer

router = APIRouter()


@router.post("/like")
async def send_message(request: Request, like: LikeRequest):
    current_user_id = await utils.get_self_id(request.cookies)
    data = {}
    data["sender_id"] = current_user_id
    data["user_id"] = like.user_id
    await broker.kafka_producer.send(topic="friends", value=json.dumps(data).encode())
    return {"status": "request sent"}


@router.get("/get_matches")
async def send_message(request: Request):
    current_user_id = await utils.get_self_id(request.cookies)
    ankets = []
    res = await database_instance.get_friends_list(current_user_id)
    for friend in res:
        anket = await database_instance.get_match_anket(friend)
        if anket:
            ankets.append(dict(anket))
    return ankets


@router.get("/get_follower")
async def get_follower(request: Request):
    current_user_id = await utils.get_self_id(request.cookies)
    follower_anket = await database_instance.get_follower(current_user_id)
    if not follower_anket:
        raise HTTPException(404)
    return FollowerAnket(
        id=follower_anket["id"],
        user_id=follower_anket["user_id"],
        name=follower_anket["name"],
        avatar=follower_anket["avatar"],
        age=follower_anket["age"],
        sex=follower_anket["sex"],
        description=follower_anket["description"],
        city=follower_anket["city"],
    )


@router.get("/followers_list")
async def get_friend_requests_receiver_list(request: Request) -> FriendRequestsList:
    current_user_id = await utils.get_self_id(request.cookies)
    requests_list = await database_instance.get_friend_receiver_requests_list(
        current_user_id
    )
    return FriendRequestsList(requests=requests_list)


@router.post("/decline_follow")
async def decline_friend_request(request: Request, follower_id: FollowerID) -> dict:
    current_user_id = await utils.get_self_id(request.cookies)
    result = await database_instance.decline_friend_request(
        follower_id.user_id, current_user_id
    )
    if result:
        return {"message": "Succesfully declined"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry....",
        )


@router.post("/accept_follow")
async def accept_friend_request(request: Request, follower_id: FollowerID) -> dict:
    current_user_id = await utils.get_self_id(request.cookies)
    result = await database_instance.accept_friend_request(
        follower_id.user_id, current_user_id
    )
    if result:
        user_tg_id = await database_instance.get_telegram_id(current_user_id)
        user_name = await database_instance.get_user_name(current_user_id)
        match_tg_id = await database_instance.get_telegram_id(follower_id.user_id)
        match_user_name = await database_instance.get_user_name(follower_id.user_id)
        data = {
            "user_id": user_tg_id,
            "match_user_id": match_tg_id,
            "user_name": user_name,
            "match_user_name": match_user_name,
        }
        await kafka_producer.send("matches", json.dumps(data).encode())
        return {"message": "Succesfully accepted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry....",
        )


"""

@router.get("/friend_list")
async def get_friend_list(request: Request) -> FriendList:
    current_user_id = await utils.get_self_id(request.cookies)
    friends_list = await database_instance.get_friends_list(current_user_id)
    return FriendList(friends=friends_list)





@router.get("/friend_requests_sender_list")
async def get_friend_requests_sender_list(request: Request) -> FriendRequestsList:
    current_user_id = await utils.get_self_id(request.cookies)
    requests_list = await database_instance.get_friend_sender_requests_list(
        current_user_id
    )
    return FriendRequestsList(requests=requests_list)


@router.post("/send_friend_request")
async def send_friend_request(request: Request, message: RequestMessage) -> dict:
    user_id = message.user_id
    current_user_id = await utils.get_self_id(request.cookies)
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't send friend request to yourself",
        )
    result = await database_instance.send_friend_request(current_user_id, user_id)
    if result:
        # notification service need to send notification to receiver of request
        await utils.send_message(request.cookies, user_id, message.message)

        return {"message": "Succesfully sended"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry....",
        )


@router.post("/cancel_friend_request")
async def cancel_friend_request(request: Request, user_id: int) -> dict:
    current_user_id = await utils.get_self_id(request.cookies)
    result = await database_instance.cancel_friend_request(current_user_id, user_id)
    if result:
        return {"message": "Succesfully canceled"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry....",
        )





@router.post("/delete_friend")
async def decline_friend_request(request: Request, user_id: int) -> dict:
    current_user_id = await utils.get_self_id(request.cookies)
    result = await database_instance.delete_friend(user_id, current_user_id)
    if result:
        return {"message": "Succesfully deleted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry....",
        )
"""
