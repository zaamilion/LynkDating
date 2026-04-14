from aiogram import types, Bot, Dispatcher
from dotenv import load_dotenv
import os
import utils
import broker

load_dotenv()
bot = Bot(token=os.getenv("tg_token"))

dp = Dispatcher()
