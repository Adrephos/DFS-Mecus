from bootstrap import HOST, PORT, LEADER, SLAVE_URL, KEEPALIVE_SLEEP_SECONDS, SYNC_PORT

from flask import Flask, request, jsonify

import bcrypt
from tinydb import TinyDB, Query

from datetime import datetime, timedelta
import threading
import time

import grpc
import NameNode_pb2_grpc
import NameNode_pb2

from concurrent import futures
from slave_service import DBService

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
# Subir la base de datos al slave
def uploadDB():
    with grpc.insecure_channel(SLAVE_URL) as channel:
        name_node_stub = NameNode_pb2_grpc.DBServiceStub(channel)

        try:
            db_bytes = open("db.json", "rb").read()
        except Exception as e:
            print(e)
            return

        request = NameNode_pb2.UploadDBRequest(db=db_bytes)
        try:
            response = name_node_stub.UploadDB(request)
        except Exception as e:
            print(e)
            return

        if response.status == "ok":
            print(response.message)
        else:
            print("Error uploading db to slave")


# Descargar la base de datos del slave
# Si es que el slave tiene una base de datos más actualizada
def downloadDB():
    with grpc.insecure_channel(SLAVE_URL) as channel:
        name_node_stub = NameNode_pb2_grpc.DBServiceStub(channel)

        request = NameNode_pb2.DownloadDBRequest(name=HOST)
        try:
            print("Requesting DB from slave")
            response = name_node_stub.DownloadDB(request)
        except Exception:
            print("Could not connect to slave")
            return

        if response.canDownload:
            try:
                file = open("db.json", "wb")
                file.write(response.db)
                file.close()
                print("DB downloaded from slave")
            except Exception as e:
                print(e)
        else:
            print("No need to download DB from slave")


# Heartbeat al slave para saber si el leader sigue vivo
def heartbeat_to_slave():
    while True:
        try:
            channel = grpc.insecure_channel(SLAVE_URL)
        except Exception as e:
            print(e)
            continue
        name_node_stub = NameNode_pb2_grpc.DBServiceStub(channel)
        request = NameNode_pb2.HeartBeatRequest(
            name=HOST, ip=HOST, port=PORT)

        try:
            name_node_stub.HeartBeat(request)
            print("Heartbeat sent to slave")
            channel.close()
        except Exception:
            print("Error sending heartbeat to slave")
        print("Waiting for next heartbeat")
        time.sleep(KEEPALIVE_SLEEP_SECONDS)


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

    uploadDB()
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

    uploadDB()
    return jsonify(response), 200


@app.route('/tree_command/<command>', methods=['POST'])
def tree_command(command):
    data = request.get_json()
    name = data.get('name')
    path = data.get('path')
    hash = data.get('hash')
    chunks = data.get('chunks')
    chunksReplicas = data.get('chunksReplicas')

    # Si el usuario no tiene un árbol, se crea uno
    # No es seguro, pero es un ejemplo
    # es para que si el servidor se cae, no se pierda el árbol
    try:
        tree = users_trees[name]
    except KeyError:
        user_tree = trees.get(Query().name == name)
        if user_tree:
            root = map_to_tree(user_tree['tree'], '/', None)
            tree = FilesTree(root)
            users_trees[name] = tree
        else:
            response = {'message': 'User does not have a tree'}
            return jsonify(response), 200

    # Comandos
    if command == 'mkdir':
        message, full_path = tree.add_dir(path)
        update_user_tree(name)
        uploadDB()
    elif command == 'cd':
        message, full_path = tree.change_dir(path)
    elif command == 'can_add':
        message, in_dir, full_path = tree.can_add_file(path)
    elif command == 'add_file':
        message, full_path = tree.add_file(path, hash, chunks, chunksReplicas)
        update_user_tree(name)
        uploadDB()

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
        elif command == 'rm':
            message, full_path = tree.rm(path)
            update_user_tree(name)
            uploadDB()
            response = {'message': message, 'full_path': full_path,
                        'curr_dir': curr_dir}
        else:
            response = {'message': 'Unknown command'}

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
        threshold_time = now - timedelta(seconds=KEEPALIVE_SLEEP_SECONDS * 2)
        for data_node in data_nodes.all():
            if 'last_seen' in data_node:
                last_seen = datetime.fromisoformat(data_node['last_seen'])
                if last_seen < threshold_time:
                    data_nodes.remove(doc_ids=[data_node.doc_id])
                    print(f"Removed inactive DataNode: {data_node['name']}")
        time.sleep(KEEPALIVE_SLEEP_SECONDS)  # Revisa cada 5 segundos


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    NameNode_pb2_grpc.add_DBServiceServicer_to_server(DBService(db), server)
    server.add_insecure_port("0.0.0.0:" + str(SYNC_PORT))
    server.start()
    print("Server started, listening on " + str(SYNC_PORT))
    server.wait_for_termination()


if __name__ == '__main__':
    threading.Thread(target=clean_up_data_nodes, daemon=True).start()
    # for the leader
    if LEADER:
        # download db from slave if possible
        downloadDB()
        # request db from slave
        threading.Thread(target=heartbeat_to_slave, daemon=True).start()
    else:
        # si es slave, levantar el servidor de grpc
        threading.Thread(target=serve, daemon=True).start()

    app.run(host=HOST, port=PORT)
