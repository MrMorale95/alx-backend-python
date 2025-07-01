from seed import connect_to_prodev

def stream_user_ages():
    conn = connect_to_prodev()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT age FROM user_data")

        for (age,) in cursor:
            yield int(age)

    except Exception as e:
        print(f"Error streaming ages: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def compute_average_age():
    total = 0
    count = 0

    for age in stream_user_ages():
        total += age
        count += 1

    if count == 0:
        print("No users found.")
    else:
        average = total / count
        print(f"Average age of users: {average:.2f}")

if __name__ == "__main__":
    compute_average_age()
