import os
import psycopg2
from dotenv import load_dotenv
import sys
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

load_dotenv(os.path.join(BASE_DIR, ".env"))

class DatabaseConnection:

    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.database = os.getenv("DB_NAME", "trainee_tracking_db")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD")
        self.port = int(os.getenv("DB_PORT", "5432"))

    def connect(self):
        try:
            connection = psycopg2.connect(
                host=self.host,
                dbname=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )

            print("Database connected successfully!")
            return connection

        except psycopg2.Error as e:
            print("Database connection failed:", e)
            return None