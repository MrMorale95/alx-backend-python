from seed import connect_to_prodev

def paginate_users(page_size, offset):

    conn = connect_to_prodev()
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
        cursor.execute(query, (page_size, offset))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Error in paginate_users: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def lazy_paginate(page_size):
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
