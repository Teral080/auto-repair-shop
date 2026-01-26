from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declared_attr
from config import Config
from datetime import datetime  

# Получаем URL из конфигурации
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

# Создаём движок для PostgreSQL 
engine = create_async_engine(DATABASE_URL, future=True, echo=False)

# Асинхронная сессия
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

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
    cars = relationship("Car", back_populates="client")

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
        }

class Car(Base, BaseMixin):
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    vin = Column(String(17), unique=True, nullable=False)
    client = relationship("Client", back_populates="cars")

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'vin': self.vin,
        }

class User(Base, BaseMixin):
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'admin', 'client', 'manager', 'master'

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
        }

# === ДОБАВЛЯЕМ ЗАПЧАСТИ ===
class Part(Base, BaseMixin):
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)  # в рублях
    stock = Column(Integer, nullable=False, default=0)  # количество на складе

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
        }

# === ДОБАВЛЯЕМ ЗАКАЗЫ С ПОДДЕРЖКОЙ ЗАПЧАСТЕЙ ===
order_part = Table(
    'order_part',
    Base.metadata,
    Column('order_id', Integer, ForeignKey('order.id'), primary_key=True),
    Column('part_id', Integer, ForeignKey('part.id'), primary_key=True),
    Column('quantity', Integer, nullable=False, default=1)
)

class Order(Base, BaseMixin):
    client_id = Column(Integer, ForeignKey('client.id'))
    user_id = Column(Integer, ForeignKey('user.id'))  # кто создал
    status = Column(String(20), default='new')  # new, in_progress, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=True)

    # Связи
    client = relationship("Client")
    user = relationship("User")
    parts = relationship("Part", secondary=order_part, back_populates="orders")

# Обратная связь для Part
Part.orders = relationship("Order", secondary=order_part, back_populates="parts")

# Утилита для создания таблиц
async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class Database:
    def __init__(self):
        self.session = async_session

    async def create_all(self):
        await create_all_tables()

db = Database()