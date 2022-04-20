from app import app, db
from app.models import User, Product
from argparse import ArgumentParser
import os, shutil

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User':User, 'Product': Product}

if __name__ == '__main__':

    parser = ArgumentParser()
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    parser.add_argument('-p', '--port', type=int, default=5000)
    parser.add_argument('-n', '--node', type=int, default=8000)
    args = parser.parse_args()
    port = args.port
    node = args.node
    app.run(host='127.0.0.1', port=port, debug=True)