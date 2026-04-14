from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, Cookie, Request, Response
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
import utils
from models import *
from dotenv import load_dotenv
from db.db_session import database_instance
from route import router

load_dotenv()

app = FastAPI()
app.include_router(router)
