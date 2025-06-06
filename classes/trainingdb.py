import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta, timezone
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