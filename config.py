from quart import Quart
from models import Car,Client

app = Quart(__name__)

app.config['SECRET_KEY'] = '1111'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///partners.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if __name__ == '__main__':
    app.run(debug=True) 