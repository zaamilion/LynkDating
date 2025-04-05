from keycloak.keycloak_admin import KeycloakAdmin
from keycloak.openid_connection import KeycloakOpenID, KeycloakOpenIDConnection
from dotenv import load_dotenv
from fastapi.security import (
    OAuth2AuthorizationCodeBearer,
)
from models import *
from typing import Annotated
import os
import keycloak
from fastapi import Depends, HTTPException, status
from db import db
import json

load_dotenv()
import os


KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
KEYCLOAK_USERNAME = os.getenv("KEYCLOAK_USERNAME")
KEYCLOAK_PASSWORD = os.getenv("KEYCLOAK_PASSWORD")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KEYCLOAK_URL}realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth",
    tokenUrl=f"{KEYCLOAK_URL}realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
)

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    realm_name=KEYCLOAK_REALM,
)
connection = KeycloakOpenIDConnection(
    server_url=KEYCLOAK_URL,
    grant_type="password",
    username=KEYCLOAK_USERNAME,
    password=KEYCLOAK_PASSWORD,
)
keycloak_admin = KeycloakAdmin(connection=connection)


async def get_user_info(token: str) -> UserInKeycloak | None:
    try:
        userinfo = await keycloak_openid.a_decode_token(
            token, keycloak_openid.a_public_key()
        )
        return UserInKeycloak(
            id=userinfo["sub"], username=userinfo["preferred_username"]
        )
    except Exception as e:
        print(e)
        return


async def refresh_token(token: str) -> Token | None:
    try:
        new_token = keycloak_openid.a_refresh_token(token)
        return Token(
            access_token=new_token["access_token"],
            refresh_token=new_token["refresh_token"],
        )
    except Exception as e:
        return


async def authenticate_user(username: str, password: str) -> UserInKeycloak | None:
    try:
        token = await keycloak_openid.a_token(username, password)
        userinfo = await get_user_info(token["access_token"])

        return userinfo
    except Exception as e:
        return None


async def register_user(username: str, password: str) -> bool:
    keycloak_id = await keycloak_signup(username, password)
    if not keycloak_id:
        return False
    if not db.signup(keycloak_id, username):
        return False
    return True


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserInKeycloak:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    userinfo = await get_user_info(token)
    if userinfo is None:
        raise credentials_exception
    return userinfo


async def keycloak_signup(username: str, password: str):
    try:
        user_id = await keycloak_admin.a_create_user(
            {
                "username": username,
                "enabled": True,
                "credentials": [
                    {
                        "type": "password",
                        "value": password,
                        "temporary": False,
                    }
                ],
            }
        )
        return user_id
    except keycloak.exceptions.KeycloakPostError as e:
        raise HTTPException(e.response_code, json.loads(e.response_body))
    except Exception as e:
        return None
