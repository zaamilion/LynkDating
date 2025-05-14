from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from db.db_session import database_instance
import redis.asyncio as redis
import utils

# Запуск Kafka Producer
r = redis.Redis(host="redis", port=6379, db=0)
kafka_producer = AIOKafkaProducer(bootstrap_servers="kafka:29092")


async def is_processed(key: bytes) -> bool:
    return bool(await r.get(key))


async def flag_as_processed(key: bytes):
    return await r.set(key, b"1", ex=3600)


async def check_access_to_send(user_id, current_user_id):
    friends_list = await database_instance.get_friends_list(current_user_id)
    if user_id not in friends_list:
        return True
    return False


async def start_kafka_consumer():
    global kafka_producer

    consumer = AIOKafkaConsumer(
        "friends",
        bootstrap_servers="kafka:29092",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.start()
    print("consumer started")
    try:
        async for msg in consumer:
            try:
                key = msg.value.decode("utf-8") + str(msg.timestamp)
                if await is_processed(key):
                    continue
                data = json.loads(msg.value.decode())
                if not await check_access_to_send(data["user_id"], data["sender_id"]):
                    continue
                await flag_as_processed(key)
                friends_requests = (
                    await database_instance.get_friend_sender_requests_list(
                        data["user_id"]
                    )
                )
                if data["sender_id"] in friends_requests:
                    await database_instance.accept_friend_request(
                        data["user_id"], data["sender_id"]
                    )
                else:
                    await database_instance.send_friend_request(
                        data["sender_id"], data["user_id"]
                    )
            except Exception as e:
                continue
    finally:
        await consumer.stop()
        print("consumer stopped ")
