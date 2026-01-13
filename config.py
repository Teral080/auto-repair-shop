from quart import Quart
from models import #Тут должны быть таблицы

app = Quart(__name__)

app.config['SECRET_KEY'] = '1111'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///partners.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False