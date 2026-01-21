# app.py
from quart import Quart
from config import Config
from routes import bp

def create_app():
    app = Quart(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config.get('SECRET_KEY') or '1111'

    # Регистрируем blueprint
    app.register_blueprint(bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)