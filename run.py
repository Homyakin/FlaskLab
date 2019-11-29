from app import app
from app import view
import os


def garbage_collector():
    files = os.listdir('./app/static')
    for i in files:
        if i.endswith('.svg'):
            os.remove(f'./app/static/{i}')


if __name__ == "__main__":
    garbage_collector()
    app.run()
