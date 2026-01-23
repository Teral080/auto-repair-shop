# app.py
from quart import Quart
from config import Config
from routes import bp
from models import async_session, User, create_all_tables
from werkzeug.security import generate_password_hash
import logging
logging.basicConfig(level=logging.WARNING)

def create_app():
    app = Quart(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config.get('SECRET_KEY') or '1111'

    from routes import bp
    app.register_blueprint(bp)

    @app.before_serving
    async def startup():
        from models import create_all_tables, async_session, User
        from sqlalchemy import select

        await create_all_tables()

        # Проверяем, есть ли админ
        async with async_session() as s:
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

