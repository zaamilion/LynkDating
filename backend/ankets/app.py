from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, Cookie, Request, Response
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from fastapi.middleware.cors import CORSMiddleware
import utils
from models import *
from dotenv import load_dotenv
import route
import broker

load_dotenv()

app = FastAPI()
app.include_router(route.router)
origins = [
    "http://localhost:3000",  # Замени на адрес твоего фронтенда
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""
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
"""
"""
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
"""


@app.on_event("startup")
async def startup():
    await broker.kafka_producer.start()
