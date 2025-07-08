import sqlite3
import functools
from functools import wraps

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('db.sqlite3')
        try:
            print(f"[CONN] started")
            return func(conn, *args, **kwargs)
        
        finally:
            print(f"[CONN] closed")
            conn.close()
    return wrapper

def transactional(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            print(f"[transaction] commited")
            return result
        except Exception as e:
            conn.rollback()
            print(f"[transaction] rollback")
            raise e
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE user_id = ?", (new_email, user_id))

# Update user's email with automatic transaction handling
# update_user_email(user_id="00000000000000000000000000000001", new_email='Crawford_Cartwright@hotmail.com')