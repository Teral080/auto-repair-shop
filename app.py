import sqlalchemy
from config import Config
from models import db
from quart import Quart, render_template, request, redirect, url_for, flash, session

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

if __name__ == '__main__':
    app.run()