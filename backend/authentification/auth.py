from keycloak.keycloak_admin import KeycloakAdmin
from keycloak.openid_connection import KeycloakOpenID, KeycloakOpenIDConnection
from fastapi.security import (
    OAuth2AuthorizationCodeBearer,
)
from models import *
from typing import Annotated
import keycloak
from fastapi import Depends, HTTPException, status
from db.db_session import database_instance
import json
import os
from configs.settings import settings

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{settings.KEYCLOAK_URL}realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/auth",
    tokenUrl=f"{settings.KEYCLOAK_URL}realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token",
)

keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_URL,
    client_id=settings.KEYCLOAK_CLIENT_ID,
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
    realm_name=settings.KEYCLOAK_REALM,
)
connection = KeycloakOpenIDConnection(
    server_url=settings.KEYCLOAK_URL,
    grant_type="password",
    username=settings.KEYCLOAK_USERNAME,
    password=settings.KEYCLOAK_PASSWORD,
)
keycloak_admin = KeycloakAdmin(connection=connection)


async def get_user_info(token: str) -> UserInKeycloak | None:
    try:
        userinfo = await keycloak_openid.a_decode_token(
            token, await keycloak_openid.a_public_key()
        )
        return UserInKeycloak(
            id=userinfo["sub"], username=userinfo["preferred_username"]
        )
    except Exception as e:
        print(e)
        return


async def refresh_token(token: str) -> Token | None:
    try:
        new_token = await keycloak_openid.a_refresh_token(token)
        return Token(
            access_token=new_token["access_token"],
            refresh_token=new_token["refresh_token"],
        )
    except Exception as e:
        return


async def authenticate_user(username: str, password: str) -> UserInKeycloak | None:
    try:
        token = await keycloak_openid.a_token(
            username,
            password,
        )
        userinfo = await get_user_info(token["access_token"])

        return userinfo
    except Exception as e:
        print(e)
        return None


async def register_user(username: str, password: str) -> bool:
    keycloak_id = await keycloak_signup(username, password)
    if not keycloak_id:
        return False
    if not await database_instance.add_user(keycloak_id, username):

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
