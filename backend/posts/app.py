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


@app.post("/create_post")
async def create_post(request: Request, response: Response, post: CreatePost):
    user_id = await utils.get_id(request.cookies)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    censure = True  # заглушка, пока не решу вопрос с цензурой
    if not censure:
        raise HTTPException(status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)

    result = db.create_post(user_id, post.description)  # return post_id
    if result:
        return {
            "message": "Post created successfully",
            "post_id": result,
        }  # return post_id
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/delete_post")
async def delete_post(request: Request, response: Response, post_id: int):
    user_id = await utils.get_id(request.cookies)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    post_author = db.get_post(post_id)[1]
    if post_author != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    result = db.delete_post(post_id)
    if result:
        return {"message": "Post deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/comment_post")
async def create_post(request: Request, response: Response, comment: CommentPost):
    user_id = await utils.get_id(request.cookies)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    friends_list = await utils.get_friends_list(request.cookies)
    post_author = db.get_post(comment.post_id)[1]
    if friends_list is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error"
        )
    elif user_id not in friends_list and post_author != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You're not friends"
        )
    result = db.comment_post(user_id, comment.post_id, comment.comment_text)
    if result:
        return {"message": "Comment created successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
