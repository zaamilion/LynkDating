import asyncio  # Для асинхронного выполнения кода
from aiogram import Bot, Dispatcher, F  # Основные компоненты aiogram
from aiogram.types import (
    Message,
    LabeledPrice,
    PreCheckoutQuery,
    SuccessfulPayment,
)  # Типы данных Telegram API
from aiogram.filters import CommandStart  # Фильтр для команды /start

# Импортируем токен бота из конфигурационного файла
from config import BOT_TOKEN

# Инициализируем бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# Обработчик команды /start
@dp.message(CommandStart())
async def start(message: Message) -> None:
    # Отправляем пользователю счет для оплаты доступа в приватный канал
    await message.answer_invoice(
        title="Доступ в приватный канал",  # Название услуги
        description="Оплата доступа в приватный канал",  # Описание услуги
        payload="access_to_privet",  # Уникальный идентификатор платежа (можно использовать для внутренней логики)
        currency="XTR",  # Валюта (проверьте, поддерживается ли она Telegram)
        prices=[LabeledPrice(label="XTR", amount=1)],  # Цена (1 XTR)
    )


# Обработчик предварительного подтверждения оплаты
@dp.pre_checkout_query()
async def checkout(event: PreCheckoutQuery) -> None:
    # Подтверждаем возможность проведения платежа
    await event.answer(True)  # True = платеж разрешен


# Обработчик успешной оплаты
@dp.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    # Создаем уникальную ссылку для вступления в приватный канал
    link = await bot.create_chat_invite_link(
        -1002696975686,  # ID чата (замените на реальный ID вашего канала)
        member_limit=1,  # Ссылка действует для одного пользователя
    )
    # возврат звезд обртно(для теста)
    await bot.refund_star_payment(
        message.from_user.id,  # ID пользователя
        message.successful_payment.telegram_payment_charge_id,  # ID платежа в Telegram
    )

    # Отправляем пользователю ссылку на канал
    await message.answer(f"твоя ссылка:\n{link.invite_link}")


# Действия при старте бота
@dp.startup()
async def on_startup() -> None:
    # Удаляем вебхук (если использовался ранее)
    await bot.delete_webhook(True)


# Запуск бота
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))  # Начинаем получать обновления от Telegram
