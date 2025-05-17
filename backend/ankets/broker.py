from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from db.db_session import database_instance
import redis.asyncio as redis
import utils

# Запуск Kafka Producer
kafka_producer = AIOKafkaProducer(bootstrap_servers="kafka:29092")
r = redis.Redis(host="redis", port=6379, db=1, decode_responses=True)


async def get_tg_by_code(key: str):
    id = await r.get(key)
    return id


redis_kafka = redis.Redis(host="redis", port=6379, db=2, decode_responses=True)


async def is_processed(key) -> bool:
    return bool(await redis_kafka.get(key))


async def flag_as_processed(key):
    return await redis_kafka.set(key, b"1", ex=3600)
