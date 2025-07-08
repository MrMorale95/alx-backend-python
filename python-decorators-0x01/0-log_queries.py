from datetime import datetime
import sqlite3
from functools import wraps

def log_queries():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            query = kwargs.get('query') or (args[0] if args else '')
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{now}] Executing SQL query: {query}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@log_queries()
def fetch_all_users(query):
    conn = sqlite3.connect('db.sqlite3')  # You might replace this with Django ORM later
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


users = fetch_all_users(query="SELECT * FROM users")
print(users)