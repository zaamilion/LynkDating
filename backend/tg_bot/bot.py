from aiogram import types, Bot, Dispatcher
from aiogram.filters import CommandStart
import asyncio
from dotenv import load_dotenv
import os
import utils
import broker
from bot_instance import dp, bot


@dp.message(CommandStart())
async def generate_code(message: types.Message):
    code = await utils.generate_code()
    await broker.fill_code(code, str(message.from_user.id))
    await message.answer(
        f"Ваш код подтверждения: `{code}`\nКод активен в течении 5 минут.",
        parse_mode="markdown",
    )


async def startup():
    kafka_task = asyncio.create_task(broker.start_kafka_consumer())
    bot_task = asyncio.create_task(dp.start_polling(bot))

    # Ждем завершения задач (на самом деле никогда не завершится)
    done, pending = await asyncio.wait(
        [kafka_task, bot_task], return_when=asyncio.FIRST_COMPLETED
    )


asyncio.run(startup())
