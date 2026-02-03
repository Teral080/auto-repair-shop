import os
from dotenv import load_dotenv 

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '1111')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql+asyncpg://postgres:postgres@localhost:5432/auto_repair'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
        # === Настройки электронной почты ===
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")       
    MAIL_DEFAULT_SENDER = 'koliawartander@gmail.com' 

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