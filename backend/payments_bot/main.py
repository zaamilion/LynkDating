import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    LabeledPrice,
    PreCheckoutQuery,
    SuccessfulPayment,
)
from aiogram.filters import CommandStart

from configs.settings import settings
import json
from db.db_session import database_instance

bot = Bot(settings.TELEGRAM_API_KEY)
dp = Dispatcher()


# Обработчик команды /start
@dp.message(CommandStart())
async def start(message: Message) -> None:
    data = message.text[6:]
    if not data:
        await message.answer("Перейдите на сайт для получения ссылки на оплату")
    data = json.loads(data)

    if message.text[6:]:
        await message.answer_invoice(
            title="Пополнение баланса",
            description="",
            payload=data["id"],
            currency="XTR",
            prices=[LabeledPrice(label="XTR", amount=data["amount"])],
        )


# Обработчик предварительного подтверждения оплаты
@dp.pre_checkout_query()
async def checkout(event: PreCheckoutQuery) -> None:
    user_id = event.invoice_payload
    if not database_instance.user_exist(int(user_id)):
        await event.answer(False, "User doesn't exists")
    await event.answer(True)


# Обработчик успешной оплаты
@dp.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    await database_instance.topup_balance(
        message.successful_payment.invoice_payload,
        message.successful_payment.total_amount,
    )
    # notifications
    if False:
        await bot.refund_star_payment(
            message.from_user.id,  # ID пользователя
            message.successful_payment.telegram_payment_charge_id,  # ID платежа в Telegram
        )


# Действия при старте бота
@dp.startup()
async def on_startup() -> None:
    # Удаляем вебхук (если использовался ранее)
    await bot.delete_webhook(True)


# Запуск бота
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))  # Начинаем получать обновления от Telegram
