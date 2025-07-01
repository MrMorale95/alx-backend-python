from seed import connect_to_prodev

def stream_users():
    conn = connect_to_prodev()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        for row in cursor:
            yield row

    except Exception as e:
        print(f"Error streaming users: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
