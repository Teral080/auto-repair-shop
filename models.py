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
    
class Car(Base, BaseMixin):
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    vin = Column(String(17), unique=True, nullable=False)

    # Связь с клиентом
    client = relationship("Client", back_populates="cars")
    # Связь с договорами (если нужно)
    contracts = relationship("Contract", back_populates="car")

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'vin': self.vin,
            'client': self.client.to_dict() if self.client else None
        }
    
# Инициализация базы данных
async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Удобный доступ к сессии
class Database:
    def __init__(self):
        self.session = async_session

    async def create_all(self):
        await create_all_tables()

db = Database()