from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

Base = declarative_base()

# Создание асинхронного движка
engine = create_async_engine(
    'sqlite+aiosqlite:///auto_repair.db', 
    echo=True,  # Логирование SQL-запросов
    future=True
)

async_session = AsyncSession(engine, expire_on_commit=False)

class BaseMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True)