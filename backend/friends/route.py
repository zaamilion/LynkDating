from fastapi import APIRouter

from fastapi import HTTPException, status, Cookie, Request, Response
import utils
from models import *
from db.db_session import database_instance

router = APIRouter()


@router.get("/friend_list")
async def get_friend_list(request: Request) -> FriendList:
    current_user_id = await utils.get_self_id(request.cookies)
    friends_list = await database_instance.get_friends_list(current_user_id)
    return FriendList(friends=friends_list)


@router.get("/friend_requests_receiver_list")
async def get_friend_requests_receiver_list(request: Request) -> FriendRequestsList:
    current_user_id = await utils.get_self_id(request.cookies)
    requests_list = await database_instance.get_friend_receiver_requests_list(
        current_user_id
    )
    return FriendRequestsList(requests=requests_list)


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


@router.post("/accept_friend_request")
async def accept_friend_request(request: Request, user_id: int) -> dict:
    current_user_id = await utils.get_self_id(request.cookies)
    result = await database_instance.accept_friend_request(user_id, current_user_id)
    if result:
        return {"message": "Succesfully accepted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry....",
        )


@router.post("/decline_friend_request")
async def decline_friend_request(request: Request, user_id: int) -> dict:
    current_user_id = await utils.get_self_id(request.cookies)
    result = await database_instance.decline_friend_request(user_id, current_user_id)
    if result:
        return {"message": "Succesfully declined"}
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
