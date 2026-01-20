import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '1111')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql+asyncpg://postgres:123456@localhost/auto_repair'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False