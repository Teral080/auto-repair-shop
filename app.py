# app.py
from quart import Quart
from config import Config
from routes import bp
from models import async_session, User, create_all_tables
from werkzeug.security import generate_password_hash
import logging
logging.basicConfig(level=logging.DEBUG)

app = Quart(__name__)

def create_app():
    app.config.from_object(Config)
    app.secret_key = app.config.get('SECRET_KEY') or '1111'

    # Регистрируем blueprint
    app.register_blueprint(bp)

    return app

@app.before_serving
async def startup():
    await create_all_tables()

    # Проверяем, есть ли админ
    async with async_session() as s:
        from sqlalchemy import select
        result = await s.execute(select(User).where(User.email == 'admin@autoservice.ru'))
        admin = result.scalar_one_or_none()
        if not admin:
            new_admin = User(
                full_name='Админ Админович',
                email='admin@autoservice.ru',
                phone='+79990000000',
                password_hash=generate_password_hash('admin'),
                role='admin'
            )
            s.add(new_admin)
            await s.commit()
            print(" Админ создан.")
            
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)

