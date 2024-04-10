import os
import requests
import socket
import hashlib
import random

import grpc
from file_transfer_pb2 import FileChunk, FileDownloadRequest
from file_transfer_pb2_grpc import FileTransferServiceStub

from bootstrap import URL, URL_SLAVE, CHUNK_SIZE


# Util Functions
def parse(message: str):
    parse_message = message.split()

    return parse_message


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except socket.error:
        return 'Unknown IP'


# Flask Functions
def available_data_nodes():
    try:
        response = requests.post(f"{URL}/available")
    except requests.exceptions.ConnectionError:
        try:
            response = requests.post(f"{URL_SLAVE}/available")
        except requests.exceptions.ConnectionError:
            print('Error when connecting to server')
            return

    available_data_nodes = []

    if response.status_code == 200:
        available_nodes = response.json()
        if available_nodes:
            print("Available DataNodes:")
            for node in available_nodes:
                available_data_nodes.append(
                    {'name': node['name'], 'ip': node['ip']})

            print(available_data_nodes)
            return available_data_nodes
        else:
            print("No available DataNodes.")
    else:
        print('Error when connecting to server')


def register_login(option, name, password, ip):
    url = f'{URL}/{option}'
    url_slave = f'{URL_SLAVE}/{option}'

    message = {'name': name, 'password': password, 'ip': ip}
    try:
        response = requests.post(url, json=message)
    except requests.exceptions.ConnectionError:
        try:
            response = requests.post(url_slave, json=message)
        except requests.exceptions.ConnectionError:
            print('Error when connecting to server')
            return

    if response.status_code == 200:
        print('Response from server:', response.json().get('response'))
        return response.json().get('response')
    else:
        print('Error when connecting to server')


def command(name, path, command):
    url = f'{URL}/tree_command/{command}'
    url_slave = f'{URL_SLAVE}/tree_command/{command}'

    message = {'name': name, 'path': path}
    try:
        response = requests.post(url, json=message)
    except requests.exceptions.ConnectionError:
        try:
            response = requests.post(url_slave, json=message)
        except requests.exceptions.ConnectionError:
            print('Error when connecting to server')
            return

    if response.status_code == 200:
        return response.json()
    else:
        print('Error when connecting to server')
        return response.json()


def add_file(name, path, hash, chunks, chunksReplicas):
    url = f'{URL}/tree_command/add_file'
    url_slave = f'{URL_SLAVE}/tree_command/add_file'

    message = {'name': name, 'path': path, 'hash': hash,
               'chunks': chunks, 'chunksReplicas': chunksReplicas}
    try:
        response = requests.post(url, json=message)
    except requests.exceptions.ConnectionError:
        try:
            response = requests.post(url_slave, json=message)
        except requests.exceptions.ConnectionError:
            print('Error when connecting to server')
            return

    if response.status_code == 200:
        return response.json()
    else:
        print('Error when connecting to server')
        return response.json()


# Client Functions
def get_filename_from_path(file_path):
    return os.path.basename(file_path)


def split_file(path: str, chunk_size: int):
    try:
        file_r = open(path, "rb")
    except Exception:
        print('not a valid file')
        return None, None
    print(os.path.basename(path))
    chunk = 0
    hash = hashlib.sha256()
    chunks = []
    byte = file_r.read(chunk_size)

    while byte:
        hash.update(byte)
        chunks.append(byte)

        byte = file_r.read(chunk_size)

        chunk += 1
    print(f'File hash: {hash.hexdigest()}')
    return hash.hexdigest(), chunks


def download_chunk(data_node_address, chunk_name):
    try:
        channel = grpc.insecure_channel(data_node_address)
        stub = FileTransferServiceStub(channel)
    except Exception:
        print(
            f"Error: DataNode {data_node_address} is not available.")
        return

    try:
        print(f'Downloading chunk from {data_node_address}')
        chunk_data = stub.Download(
            FileDownloadRequest(filename=chunk_name)).data
        return chunk_data
    except Exception:
        print(
            f"Error: Chunk download failed from {data_node_address}.")
        return None
    finally:
        channel.close()


def download_file(user, dfs_path: str, local_path: str):
    if os.path.isdir(local_path):
        print(
            f"Error: '{local_path}' is a directory, a filename is expected")
        return
    directory = os.path.dirname(local_path)
    if directory and not os.path.exists(directory):
        print(f"Creating '{directory}' directory for the downloaded file")
        os.makedirs(directory, exist_ok=True)

    # Get chunks URLs
    response = command(user, dfs_path, 'file_info')
    message = response.get('message')
    if message != "":
        print(message)
        return

    file_info = response.get('file_info')
    hash_original = file_info.get('hash')
    chunks = file_info.get('chunks')
    chunksReplicas = file_info.get('chunksReplicas')

    # Start chunks download
    try:
        f = open(local_path, 'wb')
    except Exception as e:
        print(f"Error: {e}")
        return

    for chunk_id in range(0, len(chunks)):
        data_node_address = chunks[str(chunk_id)]
        chunk_name = f"{user}_$%s.chunk{chunk_id}" % dfs_path.split('/')[-1]
        chunk_data = download_chunk(data_node_address, chunk_name)
        if not chunk_data:
            data_node_address = chunksReplicas[str(chunk_id)]
            chunk_data = download_chunk(data_node_address, chunk_name)
            if not chunk_data:
                print(
                    f"Error: DataNode {data_node_address} is not available.")
                return
        f.write(chunk_data)
    f.close()

    try:
        f = open(local_path, 'rb')
    except Exception as e:
        print(f"Error: {e}")
        return

    # Verify file hash
    data = f.read()
    hash_final = hashlib.sha256(data).hexdigest()
    if hash_final != hash_original:
        print("Error: File hash mismatch. Download failed or file is corrupted.")
    else:
        print("File downloaded and verified successfully")
    f.close()


def upload_chunk(user, full_path, nodes, chunk_id, chunk_data, hash):
    data_node = random.choice(nodes)
    data_node_ip = data_node['ip']

    with grpc.insecure_channel(f'{data_node_ip}') as channel:
        stub = FileTransferServiceStub(channel)

        last_full_path = full_path.replace('/', '$')

        chunk = FileChunk(
            filename=f'{user}_{last_full_path}',
            chunk_id=chunk_id,
            data=chunk_data,
            replicate=True,
            hash=hash
        )

        return stub.Upload(chunk), data_node


def upload_file(user, dfs_path: str, local_path: str, nodes):
    file_name = os.path.basename(local_path)
    if dfs_path[-1] != '/':
        dfs_path += '/'
    dfs_path += file_name

    response = command(user, dfs_path, 'can_add')
    message = response.get('message')
    if message != "":
        print(message)
        return
    full_path = response.get('full_path')

    print("File will be uploaded to:", full_path)

    hash, chunks = split_file(local_path, CHUNK_SIZE)
    if not hash:
        print('Error when splitting file')
        return

    # Send chunks to data-nodes
    ip_chunks = {}
    ip_chunks_replicas = {}
    for chunk_id, chunk_data in enumerate(chunks):

        response, data_node = upload_chunk(user, full_path, nodes,
                                           chunk_id, chunk_data, hash)

        if response.success:
            ip_chunks[chunk_id] = data_node['ip']
            ip_chunks_replicas[chunk_id] = response.replica_url
            print(
                f"Chunk {chunk_id} sent to {data_node['name']} successfully")
        else:
            print(
                f"Error sending chunk {chunk_id} to {data_node['name']}: {response.message}")
            return

    add_file(user, full_path, hash, ip_chunks, ip_chunks_replicas)


def run():
    login_flag = False
    user = ""
    print("\u001b[32m")
    print("  ____  _____ ____        __  __                     ")
    print(" |  _ \\|  ___/ ___|      |  \\/  | ___  ___ _   _ ___ ")
    print(" | | | | |_  \\___ \\ _____| |\\/| |/ _ \\/ __| | | / __|")
    print(" | |_| |  _|  ___) |_____| |  | |  __/ (__| |_| \\__ \\")
    print(" |____/|_|   |____/      |_|  |_|\\___|\\___|\\__,_|___/")

    curr_dir = ''
    prompt = '\n\u001b[31mPlease login or register to continue\n\u001b[36mType "help" for more information'
    data_nodes = []

    while True:
        print(
            prompt + f'\u001b[33m{curr_dir}')
        user_input = input("\u001b[35m> \u001b[37m")

        args = parse(user_input)
        if not args:
            continue

        if login_flag:
            if args[0] == 'available':
                data_nodes = available_data_nodes()
            if args[0] == 'upload':
                if len(args) != 3:
                    print("Usage: upload <file_path_in_dfs> <local_file_path>")
                elif len(args) == 3:
                    data_nodes = available_data_nodes()
                    if len(data_nodes) >= 1:
                        upload_file(user, args[1], args[2], data_nodes)
                    else:
                        print("No DataNodes available, cannot upload files :(")

            elif args[0] == 'download':
                if len(args) != 3:
                    print("Usage: download <file_path_in_dfs> <local_file_path>")
                else:
                    download_file(user, args[1], args[2])

            elif args[0] == 'mkdir':
                if len(args) != 2:
                    print("Usage: add_dir <directory_path>")
                else:
                    response = command(user, args[1], 'mkdir')
                    message = response.get('message')
                    curr_dir = response.get('curr_dir')
                    print(message, end="")

            elif args[0] == 'rm':
                if len(args) != 2:
                    print("Usage: rm <directory_path>")
                else:
                    response = command(user, args[1], 'rm')
                    message = response.get('message')
                    curr_dir = response.get('curr_dir')
                    print(message, end="")

            elif args[0] == 'cd':
                if len(args) != 2:
                    print("Usage: cd <directory_path>")
                else:
                    response = command(user, args[1], 'cd')
                    message = response.get('message')
                    curr_dir = response.get('curr_dir')
                    print(message, end="")

            elif args[0] == 'pwd':
                if len(args) != 1:
                    print("Usage: pwd")
                else:
                    response = command(user, "", 'pwd')
                    full_path = response.get('curr_dir')
                    print(full_path)

            # This is only used for testing when a file is going to be sent
            elif args[0] == 'file_info':
                if len(args) != 2:
                    print("Usage: file_info <file_path>")
                else:
                    response = command(user, args[1], 'file_info')
                    message = response.get('message')
                    curr_dir = response.get('curr_dir')
                    file_info = response.get('file_info')
                    if file_info is not None:
                        print('   hash ->', file_info['hash'])
                        print('   chunks ->', file_info['chunks'])
                        print('   chunksReplicas ->', file_info['chunksReplicas'])

                    print(message, end="")

            elif args[0] == 'ls':
                if len(args) == 1:
                    response = command(user, ".", 'ls')
                elif len(args) >= 1:
                    response = command(user, args[1], 'ls')
                else:
                    print("Usage: ls <directory_path>(optional)")
                    continue
                message = response.get('message')
                items = response.get('items')
                curr_dir = response.get('curr_dir')
                if items:
                    print("\n".join(items))
                elif message != "":
                    print(message, end="")
                else:
                    print("Directory is empty")

            elif args[0] == 'logout':
                print("Ending program...")
                break

            elif args[0] == 'help' and len(args) == 1:
                print('available commands:')
                print("  cd <path>                                   - Change directory")
                print('  clear                                       - Clear the screen')
                print('  upload <path_in_dfs> <local_file_path>      - Upload a file')
                print('  download <path_in_dfs> <local_file_path>    - Download a file')
                print('  help                                        - Show this help')
                print(
                    '  pwd                                         - Show current directory')
                print(
                    '  rm                                          - Remove file or directory reference')
                print('  logout                                      - Stop program')
                print(
                    "  ls                                          - List directory contents")
                print(
                    "  mkdir <path>                                - Create a directory")

            elif args[0] == 'clear':
                os.system('clear')

            else:
                print('Unknown command. Enter "help" for more information.')

        elif args[0] == 'login' and len(args) == 3:
            login = register_login(
                "login", args[1], args[2], str(get_ip()))
            if login == 'Successful login':
                login_flag = True
                user = args[1]
                curr_dir = '/'
                print(f'\n\u001b[34mWelcome {user}')
                prompt = "\u001b[32mCurrent Directory: "

        elif args[0] == 'register' and len(args) == 3:
            register = register_login(
                "register", args[1], args[2], str(get_ip()))
            if register == 'Successful registration':
                login_flag = True
                user = args[1]
                curr_dir = '/'
                print(f'\n\u001b[34mWelcome {user}')
                prompt = "\u001b[32mCurrent Directory: "

        elif args[0] == 'clear':
            os.system('clear')

        elif args[0] == 'help' and len(args) == 1:
            print('available commands:')
            print('  help                       - Show this help')
            print('  clear                      - Clear the screen')
            print('  login <name> <password>    - Just a simple login')
            print('  register <name> <password> - Just a simple register')

        else:
            print('Unknown command. Enter "help" for more information.')


if __name__ == '__main__':
    run()
