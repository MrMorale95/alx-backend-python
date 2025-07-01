from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    conn = connect_to_prodev()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        batch = []
        for row in cursor:
            batch.append(row)
            if len(batch) == batch_size:
                yield batch
                batch = []

        # Yield any remaining users
        if batch:
            yield batch

    except Exception as e:
        print(f"Error streaming batches: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def batch_processing(batch_size):
    for batch in stream_users_in_batches(batch_size):
        filtered = [user for user in batch if int(user['age']) > 25]
        yield filtered
