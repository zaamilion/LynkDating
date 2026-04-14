from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from db.db_session import database_instance
import redis.asyncio as redis
import utils

# Запуск Kafka Producer
r = redis.Redis(host="localhost", port=6379, db=0)
kafka_producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")


async def is_processed(key: bytes) -> bool:
    return bool(await r.get(key))


async def flag_as_processed(key: bytes):
    return await r.set(key, b"1", ex=3600)


async def check_access_to_send(cookie, user_id, current_user_id):
    friends_list = await utils.get_friends_list(cookie)
    requests_list = await utils.get_friends_requests_receiver_list(cookie)

    chat = await database_instance.get_chat_id(current_user_id, user_id)
    print("25 chat ", chat)
    if (
        (user_id not in friends_list)
        and (user_id not in requests_list)
        and (chat is not None)
    ):
        return False
    if not chat:
        await database_instance.create_chat(current_user_id, user_id)
    return True


async def start_kafka_consumer():
    global kafka_producer

    consumer = AIOKafkaConsumer(
        "chat",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                key = msg.value.decode("utf-8") + str(msg.timestamp)
                if await is_processed(key):
                    continue

                data = json.loads(msg.value.decode())
                data["cookie"] = data.get("cookie", {})
                if not await check_access_to_send(
                    data["cookie"], data["user_id"], data["sender_id"]
                ):
                    continue
                chat_id = await database_instance.get_chat_id(
                    data["sender_id"], data["user_id"]
                )
                if not chat_id:
                    continue
                chat_id = (chat_id[0])["chat_id"]
                await database_instance.send_message(
                    chat_id, {"id": data["sender_id"], "text": data["text"]}
                )
                await flag_as_processed(key)
            except Exception as e:
                raise e
    finally:
        await consumer.stop()
        print("consumer stopped ")
