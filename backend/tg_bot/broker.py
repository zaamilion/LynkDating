import redis.asyncio as redis
from aiokafka import AIOKafkaConsumer
import json
import redis.asyncio as redis
import utils
from bot_instance import bot

r = redis.Redis(host="redis", port=6379, db=1, decode_responses=True)


async def fill_code(key, tg_id):
    await r.set(key, tg_id, ex=600)


redis_kafka = redis.Redis(host="redis", port=6379, db=2)


async def is_processed(key: str) -> bool:
    return bool(await r.get(key))


async def flag_as_processed(key: str):
    return await r.set(key, b"1", ex=3600)


async def start_kafka_consumer():
    global kafka_producer

    consumer = AIOKafkaConsumer(
        "matches",
        bootstrap_servers="kafka:29092",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.start()
    try:
        async for msg in consumer:
            print("new msg")
            try:
                key = msg.value.decode("utf-8") + str(msg.timestamp)
                if await is_processed(key):
                    continue
                data = json.loads(msg.value.decode())
                print(data)
                try:
                    user_id = data["user_id"]
                    match_user_id = data["match_user_id"]
                    user_name = data["user_name"]
                    match_user_name = data["match_user_name"]
                except:
                    continue
                link_1 = utils.get_user_link(match_user_name, match_user_id)
                link_2 = utils.get_user_link(user_name, user_id)
                msg_1 = f"У вас новый мэтч! {link_1}"
                msg_2 = f"У вас новый мэтч! {link_2}"
                try:
                    await bot.send_message(user_id, msg_1, parse_mode="markdown")
                    await bot.send_message(match_user_id, msg_2, parse_mode="markdown")
                except:
                    pass
                await flag_as_processed(key)
            except Exception as e:
                raise e
                continue
    finally:
        await consumer.stop()
        print("consumer stopped ")
