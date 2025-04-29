import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import settings


# Connection config
DB_CONFIG = {
    'host': settings.DB_HOST,
    'port': settings.DB_PORT,
    'user': settings.DB_USER,
    'password': settings.DB_PASS,
    'database': settings.DB_NAME
}


def connect():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def insert_ping(chatter_id: str, model_channel_id: str):
    conn = connect()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO chatter_ci_ping (chatter_id, model_channel_id, timestamp)
        VALUES (%s, %s, NOW())
        """
        cursor.execute(query, (chatter_id, model_channel_id))
        conn.commit()
    except Error as e:
        print(f"Insert error: {e}")
    finally:
        cursor.close()
        conn.close()


def get_old_pings(minutes: int):
    conn = connect()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        query = """
        SELECT chatter_id, model_channel_id
        FROM chatter_ci_ping
        WHERE timestamp < NOW() - INTERVAL %s MINUTE
        """
        cursor.execute(query, (minutes,))
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"Query error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
        
        
def delete_ping(chatter_id: str, model_channel_id: str):
    conn = connect()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        query = """
        DELETE FROM chatter_ci_ping
        WHERE chatter_id = %s AND model_channel_id = %s
        """
        cursor.execute(query, (chatter_id, model_channel_id))
        conn.commit()
    except Error as e:
        print(f"Delete error: {e}")
    finally:
        cursor.close()
        conn.close()
        

def sign_nda(user_id: str, discord_nick: str, full_name: str):
    conn = connect()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        # Check if user already exists in the 'nda_signed' table
        check_query = """
        SELECT COUNT(*)
        FROM nda_signed
        WHERE user_id = %s
        """
        cursor.execute(check_query, (user_id,))
        count = cursor.fetchone()[0]

        if count == 0:  # User doesn't exist, so insert
            insert_query = """
            INSERT INTO nda_signed (user_id, discord_nick, full_name, sign_time)
            VALUES (%s, %s, %s, NOW())
            """
            cursor.execute(insert_query, (user_id, discord_nick, full_name))
            conn.commit()
            print(f"User {user_id} inserted into nda_signed.")
        else:
            print(f"User {user_id} already exists. Skipping insertion.")

    except Error as e:
        raise e
    finally:
        cursor.close()
        conn.close()


def is_nda_signed(user_id: str):
    conn = connect()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        query = """
        SELECT COUNT(*)
        FROM nda_signed
        WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        count = cursor.fetchone()[0]
        return count > 0  # Return True if the user exists
    except Error as e:
        print(f"Query error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()