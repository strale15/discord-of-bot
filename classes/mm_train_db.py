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
    
def insert_mm_train(trainee_id: str):
    conn = connect()
    if not conn:
        return None

    try:
        cursor = conn.cursor()

        id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        hw_id = int(now.timestamp())

        query = """
        INSERT INTO mm_train (id, trainee_id, schedule_date, hw_id)
        VALUES (%s, %s, %s, %s)
        """

        values = (id, trainee_id, now, hw_id)

        cursor.execute(query, values)
        conn.commit()

        return hw_id

    except Error as e:
        log.warning(f"Error inserting into mm_train: {e}")
        return None

    finally:
        cursor.close()
        conn.close()
        
def submit_next_mm(hw_id: str, trainee_id: str, mm_msg: str) -> int:
    conn = connect()
    if not conn:
        return 0  # Changed from False to 0 to match return type

    try:
        cursor = conn.cursor(dictionary=True)

        # Check existing MMs
        select_query = """
        SELECT mm1, mm2, mm3, mm4, mm5, schedule_date FROM mm_train
        WHERE hw_id = %s AND trainee_id = %s
        LIMIT 1
        """
        cursor.execute(select_query, (hw_id, trainee_id))
        row = cursor.fetchone()

        if not row:  # No matching record found
            return 0
        
        schedule_date = row['schedule_date'].replace(tzinfo=timezone.utc)
        
        mms = [mm for mm in [row['mm1'], row['mm2'], row['mm3'], row['mm4'], row['mm5']] if mm is not None]

        if len(mms) == 5:  # All fields are filled
            return None, schedule_date
        
        # Fixed UPDATE query - removed trailing comma
        update_query = f"""
        UPDATE mm_train
        SET mm{len(mms)+1} = %s
        WHERE hw_id = %s AND trainee_id = %s
        """
        cursor.execute(update_query, (mm_msg, hw_id, trainee_id))
        conn.commit()

        mms.append(mm_msg)
        return mms, schedule_date

    except Error as e:
        log.warning(f"Error submitting MM: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()
        
def is_mm_hw_assigned_and_not_completed(hw_id: str, trainee_id: str) -> bool:
    conn = connect()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        query = """
        SELECT 1 FROM mm_train
        WHERE trainee_id = %s AND hw_id = %s
        LIMIT 1
        """
        cursor.execute(query, (trainee_id, hw_id))
        result = cursor.fetchone()

        return result is not None  # True if a matching row exists

    except Error as e:
        log.warning(f"Error checking mm_train: {e}")
        return False

    finally:
        cursor.close()
        conn.close()
        
def get_left_mm_for_trainee_id(trainee_id: str) -> list[tuple[str, int]]:
    conn = connect()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        query = """
        SELECT 
            hw_id,
            (mm1 IS NULL) + (mm2 IS NULL) + (mm3 IS NULL) + (mm4 IS NULL) + (mm5 IS NULL) AS null_count
        FROM 
            mm_train
        WHERE 
            trainee_id = %s
            AND (mm1 IS NULL OR mm2 IS NULL OR mm3 IS NULL OR mm4 IS NULL OR mm5 IS NULL)
        """
        cursor.execute(query, (trainee_id,))  # Fixed: Added comma for tuple
        results = cursor.fetchall()
        return results  # Only returns tuples where null_count > 0

    except Error as e:
        log.warning(f"Error fetching hw_ids with null counts: {e}")
        return []

    finally:
        cursor.close()
        conn.close()