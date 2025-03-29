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


@app.get("/get_profile")
async def get_profile(request: Request, response: Response, user_id: int) -> Profile:
    me_id = await utils.get_id(request.cookies)
    if me_id != user_id:
        friends_list = await utils.get_friends_list(request.cookies)
        if not friends_list:
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error"
            )
        elif user_id not in friends_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You're not friends"
            )
    profile_id = db.get_profile_id(user_id)
    if not profile_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Profile doesn't exist"
        )
    profile = db.get_profile(profile_id)
    return Profile(
        name=profile[0], avatar=profile[1], age=profile[2], description=profile[3]
    )


@app.post("/create_profile")
async def create_profile(
    request: Request, response: Response, profile: Profile
) -> ProfileID:
    user_id = await utils.get_id(request.cookies)
    if db.get_profile_id(user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="profile already exists"
        )
    if db.create_profile(
        user_id, profile.name, profile.avatar, profile.age, profile.description
    ):

        return ProfileID(id=db.get_profile_id(user_id))


@app.post("/edit_profile")
async def cdit_profile(
    request: Request, response: Response, profile: Profile
) -> ProfileID:
    user_id = await utils.get_id(request.cookies)
    if not db.get_profile_id(user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="profile isn't    exist",
        )
    if db.edit_profile(
        user_id, profile.name, profile.avatar, profile.age, profile.description
    ):

        return ProfileID(id=db.get_profile_id(user_id))
