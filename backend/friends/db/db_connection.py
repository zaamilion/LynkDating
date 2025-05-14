from configs.settings import settings
import asyncpg
from fastapi import HTTPException


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

    async def execute(self, query: str, *args):
        """Выполняет SQL запрос"""
        if not self._connection_pool:
            await self.connect()

        self.con = await self._connection_pool.acquire()
        try:
            result = await self.con.fetch(query, *args)
            return result
        except Exception as e:
            print(e)
        finally:
            await self._connection_pool.release(self.con)

    async def user_exist(self, user_id: int) -> bool:
        result = await self.execute(f"SELECT 1 FROM users WHERE id = {user_id};")
        return bool(result)

    async def get_friends_list(self, user_id: int) -> list:
        query = """
        SELECT id, FRIEND_1 AS friend_id
    FROM friends
    WHERE FRIEND_2 = {user_id}

    UNION ALL

    SELECT id, FRIEND_2 AS friend_id
    FROM friends
    WHERE FRIEND_1 = {user_id}

    ORDER BY id DESC;
    """.format(
            user_id=user_id
        )
        result = await self.execute(query)
        if result:
            return [row["friend_id"] for row in result]
        return []

    async def get_friend_receiver_requests_list(self, user_id: int) -> list:
        query = f"SELECT sender_id FROM friends_requests WHERE user_id = {user_id};"
        result = await self.execute(query)
        if result:
            return [row["sender_id"] for row in result]
        return []

    async def get_friend_sender_requests_list(self, user_id: int) -> list:
        query = f"SELECT user_id FROM friends_requests WHERE sender_id = {user_id};"
        result = await self.execute(query)
        if result:
            return [row["user_id"] for row in result]
        return []

    async def send_friend_request(
        self, sender_id: int, receiver_id: int
    ) -> bool | None:
        # Проверяем, существует ли получатель
        if not await self.user_exist(receiver_id):
            raise HTTPException(status_code=400, detail="User doesn't exist")
        sender_requests = await self.get_friend_sender_requests_list(sender_id)
        receiver_requests = await self.get_friend_receiver_requests_list(sender_id)
        friends_list = await self.get_friends_list(sender_id)
        if receiver_id in receiver_requests:
            return await self.accept_friend_request(receiver_id, sender_id)
        if receiver_id in sender_requests:
            raise HTTPException(status_code=409, detail="Request already exists")
        if receiver_id in friends_list:
            raise HTTPException(status_code=409, detail="User is already a friend")

        # Отправляем заявку в друзья
        insert_query = """
            INSERT INTO friends_requests (USER_ID, SENDER_ID) 
            VALUES ({receiver_id}, {sender_id});
        """.format(
            receiver_id=receiver_id, sender_id=sender_id
        )
        await self.execute(insert_query)
        return True

    async def cancel_friend_request(self, sender_id: int, user_id: int) -> bool:
        """Отменяет заявку в друзья."""
        try:
            # Проверяем существование заявки
            query = """
                SELECT 1 FROM friends_requests 
                WHERE USER_ID = {user_id} AND SENDER_ID = {sender_id};
            """.format(
                user_id=user_id, sender_id=sender_id
            )
            result = await self.execute(query)

            # Если ничего не удалено, заявка не существует
            if not result:
                raise HTTPException(status_code=409, detail="Request doesn't exist")
            query = """
                DELETE FROM friends_requests
                WHERE USER_ID = {user_id} AND SENDER_ID = {sender_id};
            """.format(
                user_id=user_id, sender_id=sender_id
            )
            result = await self.execute(query)
            return True

        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    async def accept_friend_request(self, sender_id: int, user_id: int) -> bool:
        """Принимает заявку в друзья."""
        try:
            delete_query = """
                DELETE FROM friends_requests
                WHERE USER_ID = {user_id} AND SENDER_ID = {sender_id};
            """.format(
                user_id=user_id, sender_id=sender_id
            )
            print(delete_query)
            delete_result = await self.execute(delete_query)
            print(delete_result)
            # Добавляем в друзья
            insert_query = """
                INSERT INTO friends (FRIEND_1, FRIEND_2)
                VALUES ({sender_id}, {user_id});
            """.format(
                sender_id=sender_id, user_id=user_id
            )
            print(insert_query)
            await self.execute(insert_query)
            return True

        except HTTPException as e:
            print(e)
            raise e
        except Exception as e:
            print(e)
            return False

    async def decline_friend_request(self, sender_id: int, user_id: int) -> bool:
        """Отклоняет заявку в друзья."""
        try:
            # Проверяем и удаляем заявку
            query = """
                DELETE FROM friends_requests
                WHERE USER_ID = {user_id} AND SENDER_ID = {sender_id};
            """.format(
                user_id=user_id, sender_id=sender_id
            )
            result = await self.execute(query)
            return True

        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    async def delete_friend(self, user1: int, user2: int) -> bool:
        """Удаляет пользователя из списка друзей."""
        try:
            # Удаляем запись о дружбе
            query = """
                DELETE FROM friends
                WHERE (FRIEND_1 = {user1} AND FRIEND_2 = {user2}) 
                OR (FRIEND_1 = {user2} AND FRIEND_2 = {user1});
            """.format(
                user1=user1, user2=user2
            )
            result = await self.execute(query)

            # Если ничего не удалено, пользователь не является другом
            if not result:
                raise HTTPException(status_code=409, detail="User is not a friend")
            return True

        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    async def get_follower(self, user_id):
        query = """SELECT 
    a.user_id,
    a.id,
    a.name,
    a.avatar,
    a.age,
    a.sex,
    a.description,
    a.city
FROM friends_requests fr
JOIN ankets a ON fr.sender_id = a.user_id
WHERE fr.user_id = $1
ORDER BY RANDOM()
LIMIT 1;"""
        result = await self.execute(query, user_id)
        if result:
            return result[0]

    async def get_match_anket(self, user_id):
        query = """SELECT id, name, age, city, avatar, telegram FROM ankets WHERE user_id=$1;"""
        result = await self.execute(query, user_id)
        if result:
            return result[0]
