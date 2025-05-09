from configs.settings import settings
import asyncpg
from fastapi import HTTPException
import json


class Database:
    def __init__(self):
        self.user = settings.POSTGRESQL_USER
        self.password = settings.POSTGRESQL_PASSWORD
        self.host = settings.POSTGRESQL_HOST
        self.port = settings.POSTGRESQL_PORT
        self.database = settings.POSTGRESQL_DBNAME
        self._cursor = None

        self._connection_pool = None
        self.con = None

    async def connect(self):
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=1,
                    max_size=10,
                    command_timeout=600,
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                )

            except Exception as e:
                print(e)

    async def execute(self, query: str):
        """Выполняет SQL запрос"""
        if not self._connection_pool:
            await self.connect()

        # ВСЕГДА берём соединение из пула
        self.con = await self._connection_pool.acquire()
        try:
            result = await self.con.fetch(query)
            return result
        except Exception as e:
            print("Ошибка выполнения запроса:", e)
            return None
        finally:
            await self._connection_pool.release(self.con)

    async def get_chat_id(self, user_1: int, user_2: int):
        query = """SELECT chat_id FROM chats_users WHERE ((user_1 = {user_1} AND user_2 = {user_2}) OR (user_1 = {user_2} AND user_2 = {user_1}));""".format(
            user_1=user_1, user_2=user_2
        )
        result = await self.execute(query)
        if result:
            return result
        return None

    async def get_chat(self, chat_id: int):
        query = """SELECT chat FROM chats WHERE CHAT_ID = {chat_id};""".format(
            chat_id=chat_id
        )
        print(query)
        result = await self.execute(query)
        if result is not None:
            return result
        return None

    async def send_message(self, chat_id: int, message: dict):
        query = """UPDATE chats
SET chat = chat || '{message}'::jsonb
WHERE chat_id = {chat_id};""".format(
            message=json.dumps(message), chat_id=chat_id
        )
        result = await self.execute(query)
        return result

    async def upload_chat(self, chat_id: int, chat: list, chat_exists=True):
        if chat_exists:
            chat = json.dumps(chat)
            query = """UPDATE chats SET chat = ('{chat}') WHERE chat_id = {chat_id};""".format(
                chat=chat, chat_id=chat_id
            )
            result = await self.execute(query)
            return result
        else:
            chat = json.dumps(chat)
            query = """INSERT INTO chats (chat_id, chat) VALUES ({chat_id}, ('{chat}'))""".format(
                chat=chat, chat_id=chat_id
            )
            result = await self.execute(query)
            return result

    async def create_chat(self, user_1: int, user_2: int):
        query = """INSERT INTO chats_users (user_1, user_2) VALUES ({user_1}, {user_2});""".format(
            user_1=user_1, user_2=user_2
        )
        await self.execute(query)
        chat_id = await self.get_chat_id(user_1, user_2)
        await self.upload_chat(chat_id[0]["chat_id"], [], chat_exists=False)
