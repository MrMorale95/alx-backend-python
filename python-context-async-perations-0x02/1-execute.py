import sqlite3

class ExecuteQuery:
    def __init__(self, query, params=()):
        self.query = query
        self.params = params
        self.conn = None
        self.results = None

    def __enter__(self):
        self.conn = sqlite3.connect('db.sqlite3')
        cursor = self.conn.cursor()
        cursor.execute(self.query, self.params)
        self.results = cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        # Do not suppress exceptions
        return False

# Usage example:
 with ExecuteQuery("SELECT * FROM age WHERE user_id > ?", (25,)) as results:
        print(results)




