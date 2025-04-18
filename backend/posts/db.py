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

    def create_post(self, user_id: int, description: str) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute(
                """INSERT INTO posts (author_id, description) VALUES (%s, %s) RETURNING id""",
                (
                    user_id,
                    description,
                ),
            )
            res = cur.fetchone()[0]
            if res:  # if the post was created
                return res
            return True
        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    def delete_post(self, post_id: int) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
            return True
        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    def comment_post(self, user_id: int, post_id: int, comment_text: str) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute(
                """INSERT INTO comments (post_id, user_id, comment) VALUES (%s, %s, %s)""",
                (
                    post_id,
                    user_id,
                    comment_text,
                ),
            )
            return True
        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    def like_post(self, post_id: int, user_id: int) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute(
                """INSERT INTO likes (post_id, user_id) VALUES (%s, %s)""",
                (
                    post_id,
                    user_id,
                ),
            )
            return True
        except HTTPException as e:
            raise e

    def like_exist(self, post_id: int, user_id: int):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                SELECT EXISTS (
                    SELECT 1
                    FROM likes
                    WHERE post_id = %s AND user_id = %s
                )
                """,
                    (post_id, user_id),
                )
                result = cur.fetchone()
                if result:
                    return result
        except HTTPException as e:
            raise e
        except Exception as e:
            return None

    def get_post(self, post_id: int) -> tuple | None:
        try:
            with self.conn.cursor() as cur:
                cur.execute("""SELECT * FROM posts WHERE id = %s""", (post_id,))
                result = cur.fetchone()
                if result:
                    return result
        except HTTPException as e:
            raise e
        except Exception as e:
            return None


db = Database()
