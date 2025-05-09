from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    expires_in: int = 300
    refresh_expires_in: int = 1800
    refresh_token: str
    token_type: str = "bearer"
    session_state: str = ""
    scope: str = ""


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id: str


class UserInKeycloak(BaseModel):
    id: str
    username: str


class UserID(BaseModel):
    id: int
