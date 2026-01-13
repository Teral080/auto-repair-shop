import Sql
from quart import Quart

app = Quart(__name__)

@app.route('/')
async def home():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()