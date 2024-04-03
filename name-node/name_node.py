from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
import bcrypt

from files_tree.files_tree import DirectoryNode, FilesTree, map_to_tree, tree_to_map

# Inicialización de la base de datos y la tabla
db = TinyDB('db.json')
clients = db.table('clients')
trees = db.table('trees')

users_trees: dict[str, FilesTree] = {}


# Inicialización y configuración de Flask
# Server
app = Flask(__name__)


def hash_and_salt(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed.decode('utf-8')


def update_user_tree(name):
    map = tree_to_map(users_trees[name].root)
    trees.update({'tree': map}, Query().name == name)


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    ip = data.get('ip')

    if not (name or password or ip):
        response = {'response': 'Unknown message.'}

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


@app.route('/ls', methods=['POST'])
def ls():
    data = request.get_json()
    name = data.get('name')
    path = data.get('path')

    print(path)

    tree = users_trees[name]

    message, items = tree.ls(path)

    curr_dir = tree.full_path(tree.curr_dir)
    response = {'message': message, 'items': items,
                'curr_dir': curr_dir}
    update_user_tree(name)
    return jsonify(response), 200


@app.route('/mkdir', methods=['POST'])
def mkdir():
    data = request.get_json()
    name = data.get('name')
    path = data.get('path')

    tree = users_trees[name]

    message, full_path = tree.add_dir(path)

    curr_dir = tree.full_path(tree.curr_dir)
    response = {'message': message,
                'full_path': full_path, 'curr_dir': curr_dir}
    update_user_tree(name)
    return jsonify(response), 200


@app.route('/cd', methods=['POST'])
def cd():
    data = request.get_json()
    name = data.get('name')
    path = data.get('path')

    tree = users_trees[name]

    message, full_path = tree.change_dir(path)

    curr_dir = tree.full_path(tree.curr_dir)
    response = {'message': message,
                'full_path': full_path, 'curr_dir': curr_dir}
    update_user_tree(name)
    return jsonify(response), 200


@app.route('/pwd', methods=['POST'])
def pwd():
    data = request.get_json()
    name = data.get('name')
    path = data.get('path')

    tree = users_trees[name]

    dir, success = tree.get_dir(path)
    full_path = tree.full_path(dir)

    curr_dir = tree.full_path(tree.curr_dir)
    response = {'message': full_path, 'curr_dir': curr_dir}
    update_user_tree(name)
    return jsonify(response), 200


@app.route('/can_add', methods=['POST'])
def can_add():
    data = request.get_json()
    name = data.get('name')
    path = data.get('path')

    tree = users_trees[name]

    message, in_dir, full_path = tree.can_add_file(path)

    curr_dir = tree.full_path(tree.curr_dir)
    response = {'message': message,
                'full_path': full_path, 'curr_dir': curr_dir}
    update_user_tree(name)
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
