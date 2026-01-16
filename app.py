import sqlalchemy
from config import Config
from models import db
from quart import Quart, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import re

app = Quart(__name__)
app.config.from_object(Config)
app.secret_key = 'auto-service-secret-key-quart'

@app.before_serving
async def startup():
    await db.create_all()  

# Инициализация данных в сессии (имитация БД)
@app.before_serving
async def startup():
    pass  

@app.before_request
async def init_session():
    if 'clients' not in session:
        session['clients'] = []
    if 'cars' not in session:
        session['cars'] = []

def init_session_data():
    """Инициализация данных в сессии при первом обращении"""
    if 'users' not in session:
        # Пример администратора (для тестирования)
        admin = {
            'id': str(uuid.uuid4()),
            'full_name': 'Админ Админович',
            'email': 'admin@autoservice.ru',
            'phone': '+79990000000',
            'password_hash': generate_password_hash('admin'),
            'role': 'admin'
        }
        session['users'] = [admin]

    if 'clients' not in session:
        session['clients'] = []

    if 'cars' not in session:
        session['cars'] = []

    if 'orders' not in session:
        session['orders'] = []

@app.before_request
async def before_request():
    init_session_data()

def find_user_by_email(email):
    return next((u for u in session['users'] if u['email'] == email), None)

def find_client(client_id):
    return next((c for c in session['clients'] if c['id'] == client_id), None)

def require_role(*allowed_roles):
    """Декоратор-заглушка (вручную проверяем роль в каждом эндпоинте)"""
    pass  # В Quart нет встроенного декоратора, делаем проверку внутри

@app.route('/')
async def index():
    clients = session.get('clients', [])
    cars = session.get('cars', [])
    return await render_template('index.html', clients=clients, cars=cars)

# Список клиентов
@app.route('/clients')
async def client_list():
    clients = session.get('clients', [])
    return await render_template('clients.html', clients=clients)

if __name__ == '__main__':
    app.run()