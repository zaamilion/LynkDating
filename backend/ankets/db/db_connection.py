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

    async def execute(self, query: str, *args):
        """Выполняет SQL запрос"""
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.fetch(query, *args)
                return result
            except Exception as e:
                raise e
            finally:
                await self._connection_pool.release(self.con)

    async def anket_exist(self, user_id: int) -> bool:
        result = await self.execute(f"SELECT 1 FROM ankets WHERE user_id = {user_id}")
        return bool(result)

    async def get_anket_id(self, user_id):
        result = await self.execute(
            f"SELECT id FROM ankets WHERE user_id = $1", user_id
        )
        print(result)
        if result:
            return result[0]["id"]

    async def create_anket(
        self,
        user_id: int,
        name: str,
        avatar="",
        age=0,
        description="",
        sex=True,
        sex_find=True,
        city="",
        lat=0.0,
        lon=0.0,
        rating=100,
    ) -> bool:
        result = await self.execute(
            f"INSERT INTO ankets (user_id, name, avatar, age, sex, sex_find, description, lat, lon, rating, city) VALUES ({user_id}, {name}, {avatar}, {age}, {sex}, {sex_find}, {description}, {lat}, {lon}, {rating}, {city});"
        )
        return True

    async def edit_anket(
        self,
        anket_id: int,
        name: str,
        avatar="",
        age=0,
        description="",
        sex=True,
        sex_find=True,
        city="",
        lat=0.0,
        lon=0.0,
    ):
        await self.execute(
            """
            UPDATE ankets 
            SET name = $1, 
                avatar = $2, 
                age = $3, 
                description = $4, 
                sex = $5, 
                sex_find = $6, 
                city = $7, 
                lat = $8, 
                lon = $9
            WHERE id = $10;
        """,
            name,
            avatar,
            age,
            description,
            sex,
            sex_find,
            city,
            lat,
            lon,
            anket_id,
        )

    async def get_anket(self, id: int):
        result = await self.execute(f"SELECT * FROM ankets WHERE id = {id};")
        if result:
            return result[0]

    async def get_matches(self, id: int):
        anket = await self.get_anket(id)
        result = await self.execute(
            """SELECT
                    id,
                    age,
                    sex,
                    sex_find, 
                    lat,
                    lon,
                    rating,
                    (0.3 * (1 - ABS(age - {})/10.0) +
                    0.2 * (1 - ABS(lat - {})/100) +
                    0.2 * (1 - ABS(lon - {})/100) +
                    0.1 * (rating/{})) AS match_score
                FROM ankets
                WHERE
                    id != {}
                    AND sex_find = {}
                    AND sex = {}
                ORDER BY match_score DESC
                LIMIT 10;""".format(
                anket["age"],
                anket["lat"],
                anket["lon"],
                anket["rating"],
                id,
                anket["sex_find"],
                anket["sex"],
            )
        )

        return result
