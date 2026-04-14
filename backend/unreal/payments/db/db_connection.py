from configs.settings import settings
import asyncpg
from asyncpg import Record


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

    async def get_balance(self, user_id: int) -> bool:

        query = """SELECT balance FROM finance WHERE user_id = {user_id};""".format(
            user_id=user_id
        )
        result = self.execute(query)
        if result:
            return result[0]["balance"]
        if self.user_exist(user_id):
            query = """INSERT INTO finance (user_id) VALUES ({user_id});""".format(
                user_id=user_id
            )
            self.execute(query)
            result = self.get_balance(user_id)
            return result

    async def get_gift(self, gift_id: int) -> Record | None:
        query = "SELECT * FROM gifts WHERE ID = {gift_id}".format(gift_id)
        result = self.execute(query)
        if result:
            return result[0]
        return None

    async def topup_balance(self, user_id: int, amount: int):
        query = """UPDATE PAYMENTS
        SET balance = balance + {amount}
        WHERE user_id = {user_id};"""
        result = await self.execute(query)
        return True

    async def buy_gift(self, gift, user_id):
        await self.topup_balance(user_id, -(gift["price"]))
        query = """INSERT INTO user_gifts (OWNER_ID, GIFT_ID, PRICE, PRICE_SELL)
        VALUES ({owner_id}, {gift_id}, {price}, {price_sell})""".format(
            owner_id=user_id,
            gift_id=gift["id"],
            price=gift["price"],
            price_sell=gift["price_sell"],
        )
        result = await self.execute(query)
        return True

    async def send_gift(self, gift, sender_id, receiver_id):
        await self.topup_balance(sender_id, -(gift["price"]))
        query = """INSERT INTO user_gifts (OWNER_ID, GIFT_ID, SENDER_ID, PRICE, PRICE_SELL)
        VALUES ({owner_id}, {gift_id}, {sender_id}, {price}, {price_sell})""".format(
            owner_id=receiver_id,
            gift_id=gift["id"],
            sender_id=sender_id,
            price=gift["price"],
            price_sell=gift["price_sell"],
        )
        result = await self.execute(query)
        return True

    async def get_user_gift(self, gift_id: int) -> Record | None:
        query = "SELECT * FROM user_gifts WHERE ID = {gift_id}".format(gift_id)
        result = self.execute(query)
        if result:
            return result[0]
        return None

    async def sell_gift(self, user_gift):
        query = """UPDATE user_gifts
        SET sold = True 
        WHERE id = {gift_id}""".format(
            user_gift["id"]
        )
        result = self.execute(query)
        await self.topup_balance(user_gift["price_sell"])
        return True
