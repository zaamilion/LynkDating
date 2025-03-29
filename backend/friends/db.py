import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from fastapi import HTTPException

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

    def user_exist(self, user_id: int) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT username FROM users WHERE ID = %s", (user_id,))
            res = cur.fetchone()
            print(res)
            if res:
                return True
            return False
        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    def get_friends_list(self, user_id: int) -> list | None:
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT FRIEND_1 FROM friends WHERE FRIEND_2 = {}".format(user_id),
            )
            res1 = cur.fetchall()
            cur.execute(
                "SELECT FRIEND_2 FROM friends WHERE FRIEND_1 = {}".format(user_id),
            )
            res2 = cur.fetchall()
            res = [x[0] for x in res1 + res2]
            return res
        except Exception as e:
            print(e)
            return None

    def get_friend_sender_requests_list(self, sender_id) -> list | None:
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT USER_ID FROM friends_requests WHERE SENDER_ID = {}".format(
                    sender_id
                )
            )
            res = cur.fetchall()
            res = [x[0] for x in res]
            return res
        except HTTPException as e:
            raise e
        except Exception as e:
            return None

    def get_friend_receiver_requests_list(self, receiver_id) -> list | None:
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT SENDER_ID FROM friends_requests WHERE USER_ID = {}".format(
                    receiver_id
                )
            )
            res = cur.fetchall()
            res = [x[0] for x in res]
            return res
        except HTTPException as e:
            raise e
        except Exception as e:
            return None

    def send_friend_request(self, sender_id, user_id) -> bool:
        try:
            cur = self.conn.cursor()
            requests_sender_list = self.get_friend_sender_requests_list(sender_id)
            requests_receive_list = self.get_friend_receiver_requests_list(sender_id)
            friends_list = self.get_friends_list(sender_id)
            if user_id in requests_receive_list:
                return self.accept_friend_request(user_id, sender_id)
            if not self.user_exist(user_id):
                raise HTTPException(status_code=400, detail="User doesn't exist")
            if requests_sender_list is None:
                raise HTTPException(status_code=500, detail="Internal server error")
            if user_id in requests_sender_list:
                raise HTTPException(status_code=409, detail="Request already exist")
            elif user_id in friends_list:
                raise HTTPException(status_code=409, detail="User is already friend")
            else:
                cur.execute(
                    """INSERT INTO friends_requests (USER_ID, SENDER_ID) 
                    VALUES (%s, %s);""",
                    (user_id, sender_id),
                )
                return True
        except HTTPException as e:
            raise e
        except Exception as e:
            print(e)
            return False

    def cancel_friend_request(self, sender_id, user_id) -> bool:
        try:
            cur = self.conn.cursor()
            requests_list = self.get_friend_sender_requests_list(sender_id)
            if requests_list is None:
                raise HTTPException(status_code=500, detail="Internal server error")
            if user_id not in requests_list:
                raise HTTPException(status_code=409, detail="Request doesn't exist")
            else:
                cur.execute(
                    """DELETE FROM friends_requests
                    WHERE USER_ID = %s AND SENDER_ID = %s;""",
                    (user_id, sender_id),
                )
                return True
        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    def accept_friend_request(self, sender_id, user_id) -> bool:
        try:
            cur = self.conn.cursor()
            requests_list = self.get_friend_sender_requests_list(sender_id)
            if requests_list is None:
                raise HTTPException(status_code=500, detail="Internal server error")
            if user_id not in requests_list:
                raise HTTPException(status_code=409, detail="Request doesn't exist")
            else:
                cur.execute(
                    """DELETE FROM friends_requests
                    WHERE USER_ID = %s AND SENDER_ID = %s;""",
                    (user_id, sender_id),
                )
                cur.execute(
                    """INSERT INTO friends (FRIEND_1, FRIEND_2) VALUES (%s, %s);""",
                    (
                        sender_id,
                        user_id,
                    ),
                )
                return True
        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    def decline_friend_request(self, sender_id, user_id) -> bool:
        try:
            cur = self.conn.cursor()
            requests_list = self.get_friend_sender_requests_list(sender_id)
            if requests_list is None:
                raise HTTPException(status_code=500, detail="Internal server error")
            if user_id not in requests_list:
                raise HTTPException(status_code=409, detail="Request doesn't exist")
            else:
                cur.execute(
                    """DELETE FROM friends_requests
                    WHERE USER_ID = %s AND SENDER_ID = %s;""",
                    (user_id, sender_id),
                )
                return True
        except HTTPException as e:
            raise e
        except Exception as e:
            return False

    def delete_friend(self, user1, user2) -> bool:
        try:
            cur = self.conn.cursor()
            friends_list = self.get_friends_list(user1)
            if friends_list is None:
                raise HTTPException(status_code=500, detail="Internal server error")
            if user2 not in friends_list:
                raise HTTPException(status_code=409, detail="Request doesn't exist")
            else:
                cur.execute(
                    """DELETE FROM friends
                    WHERE (friend_1 = %s AND friend_2 = %s) OR (friend_2 = %s AND friend_1 = %s);""",
                    (
                        user1,
                        user2,
                        user1,
                        user2,
                    ),
                )
                return True
        except HTTPException as e:
            raise e
        except Exception as e:
            return False


db = Database()
