# routes.py
from quart import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import re

# Создаём Blueprint
bp = Blueprint('main', __name__)

def find_user_by_email(email):
    return next((u for u in session.get('users', []) if u['email'] == email), None)

def find_client(client_id):
    return next((c for c in session.get('clients', []) if c['id'] == client_id), None)

def init_session_data():
    """Инициализация данных в сессии при первом обращении"""
    if 'users' not in session:
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

@bp.before_app_request
async def before_request():
    init_session_data()

# Главная страница
@bp.route('/')
async def index():
    return await render_template('index.html')

# Регистрация
@bp.route('/register', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        form = await request.form
        full_name = form.get('full_name', '').strip()
        email = form.get('email', '').strip()
        phone = form.get('phone', '').strip()
        password = form.get('password', '')
        confirm_password = form.get('confirm_password', '')

        if not all([full_name, email, phone, password]):
            await flash('Все поля обязательны!', 'danger')
            return await render_template('reg.html')

        if password != confirm_password:
            await flash('Пароли не совпадают!', 'danger')
            return await render_template('reg.html')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            await flash('Некорректный email!', 'danger')
            return await render_template('reg.html')

        if find_user_by_email(email):
            await flash('Пользователь с таким email уже существует!', 'danger')
            return await render_template('reg.html')

        new_user = {
            'id': str(uuid.uuid4()),
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'password_hash': generate_password_hash(password),
            'role': 'client'
        }

        session['users'].append(new_user)
        await flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('main.login'))

    return await render_template('reg.html')

# Вход
@bp.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        form = await request.form
        email = form.get('email')
        password = form.get('password')

        user = find_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_role'] = user['role']
            await flash(f'Добро пожаловать, {user["full_name"]}!', 'success')
            return redirect(url_for('main.index'))
        else:
            await flash('Неверный email или пароль', 'danger')

    return await render_template('login.html')

# Выход
@bp.route('/logout')
async def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    await flash('Вы вышли из системы.', 'info')
    return redirect(url_for('main.index'))

# Список клиентов (только для персонала)
@bp.route('/clients')
async def client_list():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))
    if session.get('user_role') not in ['admin', 'manager', 'master']:
        await flash('У вас нет доступа к этому разделу.', 'warning')
        return redirect(url_for('main.index'))

    clients = session['clients']
    return await render_template('clients.html', clients=clients)

# Добавление клиента
@bp.route('/clients/add', methods=['GET', 'POST'])
async def add_client():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))
    if session.get('user_role') not in ['admin', 'manager', 'master']:
        await flash('У вас нет прав на добавление клиентов.', 'warning')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        form = await request.form
        full_name = form.get('full_name', '').strip()
        phone = form.get('phone', '').strip()
        email = form.get('email', '').strip()
        address = form.get('address', '').strip()

        if not full_name or not phone:
            await flash('ФИО и телефон обязательны!', 'danger')
            return await render_template('client_form.html', editing=False)

        new_client = {
            'id': str(uuid.uuid4()),
            'full_name': full_name,
            'phone': phone,
            'email': email,
            'address': address
        }
        session['clients'].append(new_client)
        await flash('Клиент успешно добавлен!', 'success')
        return redirect(url_for('main.client_list'))

    return await render_template('client_form.html', editing=False)

# Добавление заказа
@bp.route('/add_order', methods=['GET', 'POST'])
async def add_order():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        await flash('Заказ успешно создан! (Демо-режим)', 'success')
        return redirect(url_for('main.index'))

    clients = session['clients']
    cars = session['cars']
    services = [
        {'id': 1, 'name': 'Замена масла', 'price': 1500},
        {'id': 2, 'name': 'Диагностика', 'price': 2000}
    ]
    parts = [
        {'id': 1, 'name': 'Масляный фильтр', 'price': 400, 'stock': 10},
        {'id': 2, 'name': 'Тормозные колодки', 'price': 2500, 'stock': 5}
    ]

    return await render_template(
        'add_order.html',
        clients=clients,
        cars=cars,
        services=services,
        parts=parts
    )

# Отчёты
@bp.route('/reports')
async def reports():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))
    if session.get('user_role') not in ['admin', 'manager', 'master']:
        await flash('У вас нет доступа к отчётам.', 'warning')
        return redirect(url_for('main.index'))

    return await render_template('reports.html')