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
    
def start_hw(img_id: str, trainee_id: str) -> bool:
    conn = connect()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        query = """
        UPDATE hw_schedule
        SET start_time = %s
        WHERE img_id = %s AND trainee_id = %s
        """
        now = datetime.now(timezone.utc)
        cursor.execute(query, (now, img_id, trainee_id))
        conn.commit()

        # Check if any row was actually updated
        return cursor.rowcount > 0

    except Error as e:
        log.warning(f"Error updating start_time: {e}")
        return False

    finally:
        cursor.close()
        conn.close()
        
def is_hw_in_progress(img_id: str, trainee_id: str) -> bool:
    conn = connect()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        query = """
        SELECT 1 FROM hw_schedule
        WHERE img_id = %s
          AND trainee_id = %s
          AND start_time IS NOT NULL
          AND end_time IS NULL
          AND completed = 0
        LIMIT 1
        """
        cursor.execute(query, (img_id, trainee_id))
        result = cursor.fetchone()

        return result is not None

    except Error as e:
        log.warning(f"Error checking hw in progress: {e}")
        return False

    finally:
        cursor.close()
        conn.close()
    
def is_hw_startable(img_id: str, trainee_id: str) -> bool:
    conn = connect()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        query = """
        SELECT 1 FROM hw_schedule
        WHERE trainee_id = %s AND img_id = %s AND completed = 0 AND start_time IS NULL
        LIMIT 1
        """
        cursor.execute(query, (trainee_id, img_id))
        result = cursor.fetchone()

        return result is not None  # True if a matching row exists

    except Error as e:
        log.warning(f"Error checking hw_schedule: {e}")
        return False

    finally:
        cursor.close()
        conn.close()
        
def end_hw(img_id: str, trainee_id: str, response: str, self_rate: int) -> bool:
    conn = connect()
    if not conn:
        return False

    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Fetch current start_time for the given img_id and trainee_id
        select_query = """
        SELECT start_time FROM hw_schedule
        WHERE img_id = %s AND trainee_id = %s AND completed = 0
        LIMIT 1
        """
        cursor.execute(select_query, (img_id, trainee_id))
        row = cursor.fetchone()

        start_time = row['start_time'].replace(tzinfo=timezone.utc)
        end_time = datetime.now(timezone.utc)
        completion_time = (end_time - start_time).total_seconds()

        completion_time = (end_time - start_time).total_seconds()

        update_query = """
        UPDATE hw_schedule
        SET end_time = %s,
            completed = 1,
            completion_time = %s,
            self_rate = %s,
            response = %s
        WHERE img_id = %s AND trainee_id = %s AND completed = 0
        """
        cursor.execute(update_query, (end_time, completion_time, self_rate, response, img_id, trainee_id))
        conn.commit()

        return start_time, img_id, trainee_id, completion_time, response

    except Error as e:
        log.warning(f"Error submitting hw: {e}")
        return False

    finally:
        cursor.close()
        conn.close()
    
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
        
def get_not_started_hw_for_trainee_id(trainee_id: str) -> list[str]:
    conn = connect()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        query = """
        SELECT img_id FROM hw_schedule
        WHERE trainee_id = %s AND completed = 0 AND start_time IS NULL
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
        
def get_started_hw_for_trainee_id(trainee_id: str) -> list[str]:
    conn = connect()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        query = """
        SELECT img_id FROM hw_schedule
        WHERE trainee_id = %s AND completed = 0 AND start_time IS NOT NULL
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