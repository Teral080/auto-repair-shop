import os
import asyncpg

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '1111')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql+asyncpg://postgres:postgres@localhost:5432/auto_repair'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

from sqlalchemy import create_engine
from config import Config

def test_db_connection():
    try:
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
        print(" Успешное подключение к базе данных!")
        connection.close()
    except Exception as e:
        print(f" Ошибка подключения: {e}")

if __name__ == "__main__":
    test_db_connection()