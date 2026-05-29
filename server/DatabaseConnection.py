import os
import psycopg2

def get_env(var_name: str) -> str:
    value = os.environ.get(var_name)
    if value is None:
        raise KeyError(f"Missing required environment variable: {var_name}")
    return value

class DatabaseConnection:
    DB_HOST = get_env("DB_HOST")
    DB_NAME = get_env("DB_NAME")
    DB_USER = get_env("DB_USER")
    DB_PASSWORD = get_env("DB_PASSWORD")

    def __init__(self):
        self.connection = psycopg2.connect(
            host=self.DB_HOST,
            database=self.DB_NAME,
            user=self.DB_USER,
            password=self.DB_PASSWORD
        )
        self.cursor = self.connection.cursor()

    def closeConnection(self):
        print("Shutting down database connection")
        self.cursor.close()
        self.connection.close()
        print("Database connection has been closed.")

    def getBigData(self) -> dict:
        return {}