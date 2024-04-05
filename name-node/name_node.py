from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
import bcrypt
from datetime import datetime, timedelta
import threading
import time

from files_tree.files_tree import DirectoryNode, FilesTree, map_to_tree, tree_to_map

# Inicialización de la base de datos y la tabla
db = TinyDB('db.json')
clients = db.table('clients')
trees = db.table('trees')
data_nodes = db.table('data_nodes')

users_trees: dict[str, FilesTree] = {}


# Inicialización y configuración de Flask
# Server
app = Flask(__name__)


# Funciones útiles
def hash_and_salt(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed.decode('utf-8')


def update_user_tree(name):
    map = tree_to_map(users_trees[name].root)
    trees.update({'tree': map}, Query().name == name)


# Funciones con los clientes

@app.route('/available', methods=['POST'])
def available():
    available_nodes = data_nodes.all()
    print(available_nodes)
    return jsonify(available_nodes), 200


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    ip = data.get('ip')

    if not (name or password or ip):
        response = {'response': 'Unknown message.'}
        return jsonify(response), 200

    user = clients.get(Query().name == name)
    if user:
        response = {'response': 'Username is already in use'}
    else:
        clients.insert(
            {'name': name, 'password': hash_and_salt(password), 'ip': ip})

        root = DirectoryNode('/', None)
        root.parent = root
        trees.insert(
            {'name': name, 'tree': tree_to_map(root)}
        )
        users_trees[name] = FilesTree(root)

        response = {'response': 'Successful registration'}

    return jsonify(response), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    ip = data.get('ip')

    if not (name or password or ip):
        response = {'response': 'Unknown message.'}
        return jsonify(response), 200

    user = clients.get(Query().name == name)
    if user:
        hash = user['password'].encode('utf-8')
        if user['ip'] != ip:
            clients.update({'ip': ip}, doc_ids=[user.doc_id])

        response = {'response': 'Successful login'}

        user_tree = trees.get(Query().name == name)
        if user_tree:
            root = map_to_tree(user_tree['tree'], '/', None)
            users_trees[user['name']] = FilesTree(root)
        if not bcrypt.checkpw(password.encode('utf-8'), hash):
            response = {'response': 'Invalid username or password'}
    else:
        response = {'response': 'Invalid username or password'}

    return jsonify(response), 200


@app.route('/tree_command/<command>', methods=['POST'])
def tree_command(command):
    data = request.get_json()
    name = data.get('name')
    path = data.get('path')

    tree = users_trees[name]

    if command == 'mkdir':
        message, full_path = tree.add_dir(path)
    elif command == 'cd':
        message, full_path = tree.change_dir(path)
    elif command == 'can_add':
        message, in_dir, full_path = tree.can_add_file(path)

    curr_dir = tree.curr_dir.name
    try:
        response = {'message': message,
                    'full_path': full_path, 'curr_dir': curr_dir}
    except Exception:
        if command == 'ls':
            message, items = tree.ls(path)
            response = {'message': message, 'items': items,
                        'curr_dir': curr_dir}
        elif command == 'pwd':
            curr_dir = tree.full_path(tree.curr_dir)
            response = {'curr_dir': curr_dir}
        elif command == 'file_info':
            message, file_info = tree.file_info(path)
            response = {'message': message, 'file_info': file_info,
                        'curr_dir': curr_dir}
        else:
            response = {'message': 'Unknown command'}

    update_user_tree(name)
    return jsonify(response), 200


# Funciones con el NameNode
@app.route('/register_dn', methods=['POST'])
def register_dn():
    data = request.get_json()
    name = data.get('name')
    ip = data.get('ip')

    if not (name or ip):
        response = {'response': 'Unknown message.'}
        return jsonify(response), 200

    data_node = data_nodes.get(Query().name == name)
    if data_node:
        response = {'response': 'DataNode name is already in use'}
    else:
        data_nodes.insert(
            {'name': name, 'ip': ip})

        response = {'response': 'Successful creation'}

    return jsonify(response), 200


@app.route('/keep_alive', methods=['POST'])
def keep_alive():
    data = request.get_json()
    name = data.get('name')

    if not name:
        response = {'response': 'Unknown DataNode.'}
        return jsonify(response), 400

    data_node = data_nodes.get(Query().name == name)
    if data_node:
        data_nodes.update(
            {'last_seen': datetime.now().isoformat()}, Query().name == name)
        response = {'response': 'KeepAlive received'}
    else:
        response = {'response': 'DataNode not registered'}
        return jsonify(response), 404

    return jsonify(response), 200


def clean_up_data_nodes():
    while True:
        now = datetime.now()
        # 10 segundos sin señales y lo considera down
        threshold_time = now - timedelta(seconds=10)
        for data_node in data_nodes.all():
            if 'last_seen' in data_node:
                last_seen = datetime.fromisoformat(data_node['last_seen'])
                if last_seen < threshold_time:
                    data_nodes.remove(doc_ids=[data_node.doc_id])
                    print(f"Removed inactive DataNode: {data_node['name']}")
        time.sleep(5)  # Revisa cada 5 segundos


if __name__ == '__main__':
    threading.Thread(target=clean_up_data_nodes, daemon=True).start()
    app.run(host='127.0.0.1', port=5000)
