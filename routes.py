# routes.py
from quart import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import re
from models import async_session, User, Client, Part, Order
from sqlalchemy import select

# Создаём Blueprint
bp = Blueprint('main', __name__)

async def get_user_by_email(email: str):
    async with async_session() as s:
        result = await s.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
async def get_all_clients():
    async with async_session() as s:
        result = await s.execute(select(Client))
        return result.scalars().all()

async def get_all_parts():
    async with async_session() as s:
        result = await s.execute(select(Part))
        return result.scalars().all()

async def create_user(full_name: str, email: str, phone: str, password: str, role: str = 'client'):
    async with async_session() as s:
        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password),
            role=role
        )
        s.add(new_user)
        await s.commit()
        await s.refresh(new_user)
        return new_user

async def create_client(full_name: str, phone: str, email: str = None, address: str = None):
    async with async_session() as s:
        new_client = Client(
            full_name=full_name,
            phone=phone,
            email=email or None,
            address=address or None
        )
        s.add(new_client)
        await s.commit()
        await s.refresh(new_client)
        return new_client
    
async def create_part(name: str, price: int, stock: int):
    async with async_session() as s:
        new_part = Part(
            name=name.strip(),
            price=price,
            stock=stock
        )
        s.add(new_part)
        await s.commit()
        await s.refresh(new_part)
        return new_part

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

        existing = await get_user_by_email(email)
        if existing:
            await flash('Пользователь с таким email уже существует!', 'danger')
            return await render_template('reg.html')

        await create_user(full_name, email, phone, password, role='client')
        await flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('main.login'))

    return await render_template('reg.html')

# Вход для клиентов
@bp.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        form = await request.form
        email = form.get('email')
        password = form.get('password')

        user = await get_user_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            if user.role in ['admin', 'manager', 'master']:
                await flash('Сотрудники должны входить через специальную форму.', 'warning')
                return await render_template('login.html')
            
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            session['user_role'] = user.role
            await flash(f'Добро пожаловать, {user.full_name}!', 'success')
            return redirect(url_for('main.index'))
        else:
            await flash('Неверный email или пароль', 'danger')

    return await render_template('login.html')

# Вход для сотрудников
@bp.route('/staff/login', methods=['GET', 'POST'])
async def staff_login():
    if request.method == 'POST':
        form = await request.form
        email = form.get('email')
        password = form.get('password')

        user = await get_user_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            if user.role not in ['admin', 'manager', 'master']:
                await flash('Только сотрудники могут использовать эту форму.', 'danger')
                return await render_template('staff_login.html')
            
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            session['user_role'] = user.role
            await flash(f'Добро пожаловать, {user.full_name}!', 'success')
            return redirect(url_for('main.index'))
        else:
            await flash('Неверный email или пароль', 'danger')

    return await render_template('staff_login.html')

@bp.route('/my_orders')
async def my_orders():
    if session.get('user_role') != 'client':
        await flash('Доступ только для клиентов.', 'danger')
        return redirect(url_for('main.index'))
    return await render_template('my_orders.html')

@bp.route('/worker_orders')
async def worker_orders():
    if session.get('user_role') not in ['master', 'admin']:
        await flash('Доступ только для мастеров.', 'danger')
        return redirect(url_for('main.index'))
    return await render_template('worker_orders.html')

@bp.route('/warehouse')
async def warehouse():
    if session.get('user_role') not in ['admin', 'manager', 'master']:
        await flash('Доступ запрещён.', 'danger')
        return redirect(url_for('main.index'))
    
    parts = await get_all_parts()  
    return await render_template('warehouse.html', parts=parts)

@bp.route('/warehouse/add', methods=['GET', 'POST'])
async def add_part():
    if session.get('user_role') not in ['admin', 'manager']:
        await flash('Только администратор и менеджер могут добавлять запчасти.', 'danger')
        return redirect(url_for('main.warehouse'))

    if request.method == 'POST':
        form = await request.form
        name = form.get('name', '').strip()
        price_str = form.get('price', '').strip()
        stock_str = form.get('stock', '').strip()

        if not name or not price_str or not stock_str:
            await flash('Все поля обязательны!', 'danger')
            return await render_template('part_form.html')

        try:
            price = int(price_str)
            stock = int(stock_str)
            if price < 0 or stock < 0:
                raise ValueError
        except ValueError:
            await flash('Цена и количество должны быть целыми неотрицательными числами.', 'danger')
            return await render_template('part_form.html')

        await create_part(name, price, stock)
        await flash(f'Запчасть "{name}" успешно добавлена на склад!', 'success')
        return redirect(url_for('main.warehouse'))

    # GET-запрос: показываем форму
    return await render_template('part_form.html')

@bp.route('/all_orders')
async def all_orders():
    if session.get('user_role') not in ['manager', 'admin']:
        await flash('Доступ запрещён.', 'danger')
        return redirect(url_for('main.index'))

    async with async_session() as s:
        result = await s.execute(
            select(Order)
            .join(Client, Order.client_id == Client.id)
            .join(User, Order.user_id == User.id)
        )
        orders = result.scalars().all()

    return await render_template('all_orders.html', orders=orders)

# Выход
@bp.route('/logout')
async def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    await flash('Вы вышли из системы.', 'info')
    return redirect(url_for('main.index'))

# Профиль
@bp.route('/profil')
async def profil():
    if 'user_id' not in session:
        await flash('Пожалуйста, войдите в систему.', 'warning')
        return redirect(url_for('main.login'))
    return await render_template('profil.html')

# Список клиентов
@bp.route('/clients')
async def client_list():
    if not session.get('user_id') or session.get('user_role') not in ['admin', 'manager', 'master']:
        await flash('У вас нет доступа к этому разделу.', 'warning')
        return redirect(url_for('main.index'))

    clients = await get_all_clients()
    return await render_template('clients.html', clients=clients)

# Список пользователей (сотрудников)
@bp.route('/users')
async def user_list():
    if session.get('user_role') != 'admin':
        await flash('Доступ запрещён', 'danger')
        return redirect(url_for('main.index'))
    
    async with async_session() as s:
        result = await s.execute(select(User))
        users = result.scalars().all()
    return await render_template('users_list.html', users=users)

# Создание сотрудника
@bp.route('/users/create', methods=['GET', 'POST'])
async def create_staff():
    if session.get('user_role') != 'admin':
        await flash('Доступ запрещён', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        form = await request.form
        full_name = form.get('full_name', '').strip()
        email = form.get('email', '').strip()
        phone = form.get('phone', '').strip()
        password = form.get('password', '')
        role = form.get('role', 'master')

        if not all([full_name, email, phone, password]):
            await flash('Все поля обязательны!', 'danger')
            return await render_template('staff_form.html')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            await flash('Некорректный email!', 'danger')
            return await render_template('staff_form.html')

        existing = await get_user_by_email(email)
        if existing:
            await flash('Пользователь с таким email уже существует!', 'danger')
            return await render_template('staff_form.html')

        if role not in ['manager', 'master']:
            await flash('Недопустимая роль!', 'danger')
            return await render_template('staff_form.html')

        await create_user(full_name, email, phone, password, role=role)
        await flash(f'Сотрудник {full_name} успешно создан!', 'success')
        return redirect(url_for('main.user_list'))

    return await render_template('staff_form.html')

# Добавление клиента
@bp.route('/clients/add', methods=['GET', 'POST'])
async def add_client():
    if not session.get('user_id') or session.get('user_role') not in ['admin', 'manager', 'master']:
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

        await create_client(full_name, phone, email or None, address or None)
        await flash('Клиент успешно добавлен!', 'success')
        return redirect(url_for('main.client_list'))

    return await render_template('client_form.html', editing=False)

@bp.route('/add_order', methods=['GET', 'POST'])
async def add_order():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        form = await request.form
        client_id = form.get('client_id')
        description = form.get('description', '').strip()

        if not client_id:
            await flash('Выберите клиента!', 'danger')
            return redirect(url_for('main.add_order'))

        try:
            client_id = int(client_id)
        except ValueError:
            await flash('Некорректный клиент!', 'danger')
            return redirect(url_for('main.add_order'))

        # Сохраняем заказ в БД
        async with async_session() as s:
            new_order = Order(
                client_id=client_id,
                user_id=session['user_id'],
                description=description,
                status='new'
            )
            s.add(new_order)
            await s.commit()

        await flash('Заказ успешно создан!', 'success')
        # Перенаправляем в зависимости от роли
        if session.get('user_role') == 'client':
            return redirect(url_for('main.my_orders'))
        else:
            return redirect(url_for('main.all_orders'))

    # GET: показываем форму с клиентами из БД
    clients = await get_all_clients()
    return await render_template('add_order.html', clients=clients)

# Отчёты
@bp.route('/reports')
async def reports():
    if not session.get('user_id') or session.get('user_role') not in ['admin', 'manager', 'master']:
        await flash('У вас нет доступа к отчётам.', 'warning')
        return redirect(url_for('main.index'))
    return await render_template('report.html',stats=session)