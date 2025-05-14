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

        self.con = await self._connection_pool.acquire()
        try:
            result = await self.con.fetch(query, *args)
            return result
        except Exception as e:
            print(e)
        finally:
            await self._connection_pool.release(self.con)

    async def execute_row(self, query: str, *args):
        """Выполняет SQL запрос"""
        if not self._connection_pool:
            await self.connect()

        self.con = await self._connection_pool.acquire()
        try:
            result = await self.con.fetchrow(query, *args)
            return result
        except Exception as e:
            print(e)
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
        telegram="",
        sex=True,
        sex_find=True,
        city="",
        lat=0.0,
        lon=0.0,
    ) -> bool:
        result = await self.execute(
            f"""INSERT INTO ankets (user_id, name, avatar, age, sex, sex_find, description, lat, lon, city, telegram)
              VALUES ($1,$2,$3,$4,$5,$6,$7, $8, $9, $10, $11); """,
            user_id,
            name,
            avatar,
            age,
            sex,
            sex_find,
            description,
            lat,
            lon,
            city,
            telegram,
        )
        return True

    async def edit_anket(
        self,
        anket_id: int,
        name: str,
        avatar="",
        age=0,
        description="",
        telegram="",
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
                lon = $9,
                telegram = $11
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
            telegram,
        )

    async def get_anket(self, id: int):
        result = await self.execute(f"SELECT * FROM ankets WHERE id = {id};")
        if result:
            return result[0]

    async def get_matches(self, id: int):
        anket = await self.get_anket(id)
        if not anket:
            return None

        query = """
        SELECT *
FROM (
        SELECT
            a.id,
            a.user_id,
            a.age,
            a.sex,
            a.sex_find,
            a.lat,
            a.lon,
            ((1 - ABS(a.age - {age})) +
            (1 - ABS(a.lat - {lat}) / 10) +
            (1 - ABS(a.lon - {lon}) / 10) -
            COALESCE(
                ROUND(
                    (1 - EXTRACT(EPOCH FROM NOW() - su.seen_at))
                )
            , 0)
            ) AS match_score
        FROM ankets a
        LEFT JOIN seen_users su ON a.id = su.seen_user_id AND su.user_id = {current_user_id}
        WHERE
            a.id != {current_user_id}
            AND a.sex = '{sex_find}'
            AND a.sex_find = '{sex}'
        ORDER BY match_score DESC
        LIMIT 3) AS top_matches
ORDER BY RANDOM()
LIMIT 1;
        """.format(
            age=anket["age"],
            lat=anket["lat"],
            lon=anket["lon"],
            current_user_id=id,
            sex_find=anket["sex_find"],
            sex=anket["sex"],
        )

        result = await self.execute(query)
        print("aaa")
        if result:
            print([(a["id"], int(a["match_score"])) for a in result])
        # Если нашли совпадение — сохраняем факт просмотра
        if result and len(result) > 0:
            matched_user_id = result[0]["id"]

            # Сохраняем в seen_users
            insert_seen = f"""
            INSERT INTO seen_users (user_id, seen_user_id)
            VALUES ({id}, {matched_user_id})
            ON CONFLICT (user_id, seen_user_id) DO UPDATE SET seen_at = CURRENT_TIMESTAMP;
            """
            await self.execute(insert_seen)

        return result
