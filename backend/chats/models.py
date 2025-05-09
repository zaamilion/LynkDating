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


class UserID(BaseModel):
    id: int


class FriendList(BaseModel):
    friends: list


class FriendRequestsList(BaseModel):
    requests: list


class Message(BaseModel):
    user_id: int
    text: str
