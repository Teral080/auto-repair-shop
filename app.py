import Sql
from quart import Quart
from config import Config

app = Quart(__name__)
app.config.from_object(Config)

@app.before_serving
async def startup():
    await db.create_all()  # Создает таблицы при запуске (для разработки)
    
@app.route('/')
async def home():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()