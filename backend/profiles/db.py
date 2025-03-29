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

    def profile_exist(self, user_id: int) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("""SELECT id FROM profiles WHERE user_id = %s""", (user_id,))
            res = cur.fetchone()
            if res:
                return True
            return False
        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    def get_profile_id(self, user_id):
        try:
            if not self.profile_exist(user_id):
                raise HTTPException(status_code=404, detail="Profile not found")
            cur = self.conn.cursor()
            cur.execute("""SELECT id FROM profiles WHERE user_id = %s""", (user_id,))
            res = cur.fetchone()
            if res:
                return res[0]
            return None
        except HTTPException as e:
            raise e
        except Exception as e:
            return None

    def create_profile(
        self, user_id, name, avatar=False, age=0, description=""
    ) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute(
                """INSERT INTO profiles (user_id, name, avatar, age, description) VALUES (%s, %s, %s, %s, %s)""",
                (user_id, name, avatar, age, description),
            )
            return True
        except Exception as e:
            return False

    def get_profile(self, profile_id):
        try:
            cur = self.conn.cursor()
            cur.execute(
                """SELECT name, avatar, age, description FROM profiles WHERE id = %s""",
                (profile_id,),
            )
            res = cur.fetchone()
            if res:
                return res
            return None
        except HTTPException as e:
            raise e
        except Exception as e:
            return None


db = Database()
