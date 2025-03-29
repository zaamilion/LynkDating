import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
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

    def get_id(self, username: str) -> int | None:
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT id FROM users WHERE username = '{}'".format(username),
            )
            res = cur.fetchone()
            if res:
                return res[0]
        except Exception as e:
            print(e)
            return None

    def get_user(self, id: int) -> tuple | None:
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT keycloak_id, username FROM users WHERE id = {}".format(id)
            )
            res = cur.fetchone()
            if res:
                return res
        except Exception as e:
            return None

    def user_exist(self, id: int) -> bool:
        try:
            cur = self.conn.cursor()

            cur.execute(
                "SELECT username FROM users WHERE id = '{}'".format(id),
            )
            res = cur.fetchone()

            if res:
                return True
            return False
        except Exception as e:
            return False

    def signup(self, keycloak_id: str, username: str) -> bool:
        if self.user_exist(username):
            return False

        try:
            cur = self.conn.cursor()

            cur.execute(
                """INSERT INTO users (keycloak_id, username)
                VALUES (%s, %s);""",
                (keycloak_id, username),
            )
            return True
        except Exception as e:
            print(e)
            return False


db = Database()
