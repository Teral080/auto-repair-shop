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

# Главная страница
@app.route('/')
async def index():
    return await render_template('index.html')

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        form = await request.form
        full_name = form.get('full_name', '').strip()
        email = form.get('email', '').strip()
        phone = form.get('phone', '').strip()
        password = form.get('password', '')
        confirm_password = form.get('confirm_password', '')

        # Валидация
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

        # Роль назначается автоматически — "client"
        new_user = {
            'id': str(uuid.uuid4()),
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'password_hash': generate_password_hash(password),
            'role': 'client'  # ←←← Клиент НЕ выбирает роль!
        }

        users = session['users']
        users.append(new_user)
        session['users'] = users

        await flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return await render_template('reg.html')
# Вход
@app.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('index'))
        else:
            await flash('Неверный email или пароль', 'danger')

    return await render_template('login.html')

# Выход
@app.route('/logout')
async def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    await flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()