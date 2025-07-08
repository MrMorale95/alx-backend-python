import sqlite3
import functools
from functools import wraps
import time

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('db.sqlite3')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    print(f"[Retry {attempt}/{retries}] Error: {e}")
                    if attempt < retries:
                        time.sleep(delay)
                    else:
                        print("[Error] All retries failed.")
                        raise
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()
