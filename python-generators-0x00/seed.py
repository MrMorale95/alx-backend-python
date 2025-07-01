import mysql.connector
import csv
import sys
import time
from mysql.connector import Error, InterfaceError

def connect_db(max_retries=3, retry_delay=2):
    attempt = 0
    while attempt < max_retries:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                connection_timeout=5
            )
            print("Successfully connected to MySQL server")
            return conn
        except (Error, InterfaceError) as e:
            attempt += 1
            print(f"Connection attempt {attempt} failed: {str(e).split('\n')[0]}")
            if attempt == max_retries:
                print("Max connection attempts reached. Exiting.")
                sys.exit(1)
            time.sleep(retry_delay)

def check_database_exists(connection, dbname):

    try:
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES LIKE %s", (dbname,))
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists
    except Error as e:
        print(f"Error checking: {e}")
        return False

def create_database(connection):
    try:
        cursor = connection.cursor()
        
        if not check_database_exists(connection, "ALX_prodev"):
            cursor.execute("CREATE DATABASE ALX_prodev")
            print("Database created successfully")
        else:
            print("ℹ Database already exists") 
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

def connect_to_prodev(max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="ALX_prodev",
                connection_timeout=5
            )
            print("Successfully connected")
            return conn
        except (Error, InterfaceError) as e:
            attempt += 1
            print(f"Connection attempt {attempt} failed: {str(e).split('\n')[0]}")
            if attempt == max_retries:
                print("Max connection attempts reached. Exiting.")
                sys.exit(1)
            time.sleep(retry_delay)

def check_table_exists(connection, table_name):
    """Check if table exists in database"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = 'ALX_prodev' 
            AND table_name = %s
        """, (table_name,))
        exists = cursor.fetchone()[0] > 0
        cursor.close()
        return exists
    except Error as e:
        print(f"❌ Error checking table existence: {e}")
        return False

def create_table(connection):
    """Create table with existence check and enhanced schema"""
    try:
        cursor = connection.cursor()
        
        if not check_table_exists(connection, "user_data"):
            cursor.execute("""
                CREATE TABLE user_data (
                    user_id VARCHAR(36) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    age DECIMAL(3,0) NOT NULL CHECK (age > 0)
                )
            """)
            print("✓ Table user_data created successfully")
        else:
            print("ℹ Table user_data already exists")
            
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")
        connection.rollback()

def insert_data(connection, filename):
    try:
        cursor = connection.cursor()
        
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            records_inserted = 0
            duplicates_skipped = 0
            errors = 0
            
            for row in reader:
                try:
                    cursor.execute("""
                        INSERT INTO user_data (user_id, name, email, age)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE user_id=user_id
                    """, (row['user_id'], row['name'], row['email'], row['age']))
                    
                    if cursor.rowcount == 1:
                        records_inserted += 1
                    else:
                        duplicates_skipped += 1
                        
                except Error as e:
                    errors += 1
                    print(f"⚠ Error inserting record {row.get('user_id', 'UNKNOWN')}: {str(e).split('\n')[0]}")
                    connection.rollback()
                    continue
            
            connection.commit()
            print(f"\nData import summary:")
            print(f"Records inserted: {records_inserted}")
            print(f"Duplicates skipped: {duplicates_skipped}")
            print(f"Errors encountered: {errors}")
            
    except (Error, IOError) as e:
        print(f"Fatal error during data import: {e}")
        connection.rollback()
    finally:
        if cursor:
            cursor.close()

if __name__ == "__main__":
    try:
        # Initial server connection
        print("\n🔗 Establishing MySQL server connection...")
        server_conn = connect_db()
        
        # Database creation
        print("\n🛠 Creating/verifying database...")
        create_database(server_conn)
        server_conn.close()
        
        # Connect to specific database
        print("\n🔗 Connecting to ALX_prodev database...")
        db_conn = connect_to_prodev()
        
        # Table creation
        print("\n🛠 Creating/verifying table...")
        create_table(db_conn)
        
        # Data insertion
        print("\n📥 Importing data from CSV...")
        insert_data(db_conn, "user_data.csv")  # Replace with your CSV path
        
    except Exception as e:
        print(f"\nFatal error: {e}")
    finally:
        if 'db_conn' in locals() and db_conn.is_connected():
            db_conn.close()
            print("\n🔌 Database connection closed")
        print("\nScript execution complete")