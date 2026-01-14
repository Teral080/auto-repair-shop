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

class Client(Base, BaseMixin):
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)

    # Связь с автомобилями
    cars = relationship("Car", back_populates="client")

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'cars': [car.to_dict() for car in self.cars]  # Вложенные данные
        }