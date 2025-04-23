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