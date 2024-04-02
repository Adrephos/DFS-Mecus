from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
import bcrypt

# Inicialización de la base de datos y la tabla
db = TinyDB('db.json')
clients = db.table('clients')


# Inicialización y configuración de Flask
# Server
app = Flask(__name__)


def hash_and_salt(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed.decode('utf-8')


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    ip = data.get('ip')

    if name and password and ip:
        user = clients.get(Query().name == name)
        if user:
            response = {'response': 'Username is already in use'}
        else:
            clients.insert(
                {'name': name, 'password': hash_and_salt(password), 'ip': ip})
            response = {'response': 'Successful registration'}
    else:
        response = {'response': 'Unknown message.'}

    return jsonify(response), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    ip = data.get('ip')

    if name and password and ip:
        user = clients.get(Query().name == name)

        if user:
            hash = str(user.get('password')).encode('utf-8')
            if not bcrypt.checkpw(password.encode('utf-8'), hash):
                response = {'response': 'Invalid username or password'}
            if user['ip'] != ip:
                clients.update({'ip': ip}, doc_ids=[user.doc_id])

            response = {'response': 'Successful login'}
        else:
            response = {'response': 'Invalid username or password'}
    else:
        response = {'response': 'Unknown message.'}

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
