from configs.settings import settings
import asyncpg


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
                    command_timeout=60,
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
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.fetch(query)
                return result
            except Exception as e:
                raise e
            finally:
                await self._connection_pool.release(self.con)

    async def get_user_id(self, username: str) -> int | None:
        """Получает id пользователя по его username"""
        result = await self.execute(
            f"SELECT id FROM users WHERE username = '{username}'"
        )
        if result:
            return result[0]["id"]

    async def get_user(self, user_id: int):
        """Получает пользователя (keycloak_id, username) по его id"""
        return await self.execute(
            f"SELECT keycloak_id, username FROM users WHERE id = {user_id}"
        )

    async def user_exist(self, user_id: int) -> bool:
        """Проверяет существует ли пользователь по его id"""
        res = await self.execute(f"SELECT username FROM users WHERE id = '{user_id}'")
        return bool(res)

    async def add_user(self, keycloak_id: str, username: str) -> bool:
        res = await self.execute(
            f"INSERT INTO users (keycloak_id, username) VALUES ('{keycloak_id}', '{username}') RETURNING id;",
        )
        return bool(res)
