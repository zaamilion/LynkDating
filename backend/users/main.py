from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from models import Token, UserID, UserInKeycloak
import auth
from db import db
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


@app.post("/auto-verify")
async def get_current_user(request: Request, response: Response) -> UserInKeycloak:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    userinfo = auth.get_user_info(token)
    if userinfo is None:
        token = refresh_token(request, response)
        userinfo = auth.get_user_info(token)
        if userinfo is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    return userinfo


@app.post("/get_user_id")
async def get_user_id(request: Request, response: Response) -> UserID:
    username = (await get_current_user(request, response)).username
    user_id = db.get_id(username)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not get user id",
        )
    return UserID(id=user_id)


@app.post("/refresh_token")
async def refresh_token(request: Request, response: Response) -> Token:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    new_token = auth.refresh_token(refresh_token)
    if new_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    response.set_cookie(key="access_token", value=new_token.access_token, httponly=True)
    response.set_cookie(
        key="refresh_token", value=new_token.refresh_token, httponly=True
    )
    return new_token


@app.post("/signin")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = auth.keycloak_openid.token(form_data.username, form_data.password)
    response.set_cookie(key="access_token", value=token["access_token"], httponly=True)
    response.set_cookie(
        key="refresh_token", value=token["refresh_token"], httponly=True
    )
    return Token(
        access_token=token["access_token"],
        refresh_token=token["refresh_token"],
        token_type="bearer",
    )


@app.post("/signup")
async def signup(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    if auth.register_user(form_data.username, form_data.password):
        return await login_for_access_token(response, form_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sorry"
        )


@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}
