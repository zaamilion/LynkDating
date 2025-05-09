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

    async def user_exist(self, user_id: int) -> bool:
        result = await self.execute(f"SELECT 1 FROM users WHERE id = {user_id};")
        return bool(result)

    async def topup_balance(self, user_id: int, amount: int):
        query = """UPDATE PAYMENTS
        SET balance = balance + {amount}
        WHERE user_id = {user_id};"""
        result = await self.execute(query)
        return True
