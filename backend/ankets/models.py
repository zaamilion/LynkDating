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


class AnketID(BaseModel):
    id: int


class Anket(BaseModel):
    name: str
    avatar: str
    age: int
    sex: bool
    sex_find: bool
    description: str
    city: str
    lat: float
    lon: float
    telegram: str


class AnketUpdate(BaseModel):
    name: str
    avatar: str
    age: int
    sex: bool
    sex_find: bool
    description: str
    city: str
    lat: float
    lon: float
    telegram: str


class MathAnketsIDS(BaseModel):
    ids: list[int]


class MatchmateAnket(BaseModel):
    id: int
    user_id: int
    name: str
    avatar: str
    age: int
    sex: bool
    description: str
    city: str


class VerificationCode(BaseModel):
    code: str


class TelegramID(BaseModel):
    id: str
