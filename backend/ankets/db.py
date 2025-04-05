import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from fastapi import HTTPException
import os

load_dotenv()

db_name = os.getenv("POSTGRESQL_DBNAME")
db_user = os.getenv("POSTGRESQL_USER")
db_password = os.getenv("POSTGRESQL_PASSWORD")
host = os.getenv("POSTGRESQL_HOST")
port = int(os.getenv("POSTGRESQL_PORT"))


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            database=db_name,
            host=host,
            user=db_user,
            password=db_password,
            port=port,
        )
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    def query(self, query):
        cur = self.conn.cursor()
        cur.execute(query)
        return cur.fetchall()

    def anket_exist(self, user_id: int) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("""SELECT id FROM ankets WHERE user_id = %s""", (user_id,))
            res = cur.fetchone()
            if res:
                return True
            return False
        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    def get_anket_id(self, user_id):
        try:
            if not self.anket_exist(user_id):
                return None
            cur = self.conn.cursor()
            cur.execute("""SELECT id FROM ankets WHERE user_id = %s""", (user_id,))
            res = cur.fetchone()
            print(res)
            if res:
                return res[0]
            return None
        except HTTPException as e:
            raise e
        except Exception as e:
            raise e

    def create_anket(
        self,
        user_id,
        name,
        avatar=False,
        age=0,
        description="",
        sex=True,
        sex_find=True,
        lat=0.0,
        lon=0.0,
        rating=100,
    ) -> bool:
        try:
            print("do")
            cur = self.conn.cursor()
            cur.execute(
                """INSERT INTO ankets (user_id, name, avatar, age, sex, sex_find, description, lat, lon, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    user_id,
                    name,
                    avatar,
                    age,
                    sex,
                    sex_find,
                    description,
                    lat,
                    lon,
                    rating,
                ),
            )
            print("sdelal")
            return True
        except Exception as e:
            raise e

    def get_anket(self, id):
        try:
            cur = self.conn.cursor()
            cur.execute(
                """SELECT name, avatar, age, sex, sex_find, description, lat, lon, rating FROM ankets WHERE id = %s""",
                (id,),
            )
            res = cur.fetchone()
            if res:
                return res
            return None
        except HTTPException as e:
            raise e
        except Exception as e:
            return None

    """' Matcmaking"""

    def get_matches(self, user_id):
        try:

            anket = self.get_anket(user_id)

            cur = self.conn.cursor()
            cur.execute(
                """SELECT
                    id,
                    age,
                    sex,
                    sex_find, 
                    lat,
                    lon,
                    rating,
                    (0.3 * (1 - ABS(age - %s)/10.0) +
                    0.2 * (1 - ABS(lat - %s)/100) +
                    0.2 * (1 - ABS(lon - %s)/100) +
                    0.1 * (rating/%s)) AS match_score
                FROM ankets
                WHERE
                    id != %s
                    AND sex_find = %s
                    AND sex = %s
                ORDER BY match_score DESC
                LIMIT 10""",
                (
                    anket[2],  # age
                    anket[6],  # lat
                    anket[7],  # lon
                    anket[8],  # rating divisor (250?)
                    user_id,
                    anket[3],  # sex_find
                    anket[4],  # sex
                ),
            )
            res = cur.fetchall()
            if res:
                return res
            return None
        except HTTPException as e:
            raise e
        except Exception as e:
            raise e


db = Database()
