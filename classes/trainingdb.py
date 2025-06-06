import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta, timezone
import uuid

import settings

# Connection config
DB_CONFIG = {
    'host': settings.DB_HOST,
    'port': settings.DB_PORT,
    'user': settings.DB_USER,
    'password': settings.DB_PASS,
    'database': settings.DB_NAME
}

log = settings.logging.getLogger()

def connect():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        log.error(f"Error connecting to MySQL: {e}")
        return None
    
def insert_hw_schedule(img_id: str, trainee_id: str):
    conn = connect()
    if not conn:
        return None

    try:
        cursor = conn.cursor()

        hw_id = str(uuid.uuid4())

        query = """
        INSERT INTO hw_schedule (id, img_id, trainee_id)
        VALUES (%s, %s, %s)
        """

        values = (hw_id, img_id, trainee_id)

        cursor.execute(query, values)
        conn.commit()

        return hw_id

    except Error as e:
        log.warning(f"Error inserting into hw_schedule: {e}")
        return None

    finally:
        cursor.close()
        conn.close()
        
def get_img_ids_for_trainee(trainee_id: str) -> list[str]:
    conn = connect()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        query = """
        SELECT img_id FROM hw_schedule
        WHERE trainee_id = %s
        """
        cursor.execute(query, (trainee_id,))
        results = cursor.fetchall()

        # Extract img_id from each row
        img_ids = [row[0] for row in results]
        return img_ids

    except Error as e:
        log.warning(f"Error fetching img_ids: {e}")
        return []

    finally:
        cursor.close()
        conn.close()