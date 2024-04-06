import os
import requests
import socket
import hashlib

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

def available():
    try:
        response = requests.post(f"{URL}/available")
    except requests.exceptions.ConnectionError:
        print('Error when connecting to server')
        return

    # MEJOR QUE GUARDE ESO COMO UN MAPA XD
    available_data_nodes = []

    if response.status_code == 200:
        # available_data_nodes.append(available_data_nodes)
        available_nodes = response.json()
        if available_nodes:
            print("Available DataNodes:")
            for node in available_nodes:
                available_data_nodes.append(
                    {'name': node['name'], 'ip': node['ip']})

                # TIENE QUE SER EN UN RETURN
            print(available_data_nodes)
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

    try:
        os.mkdir('./chunks')
    except Exception:
        print('./chunks/ already exists')

    while byte:
        hash.update(byte)
        chunks.append(byte)
        # PUEDE MANDAR LOS BYTES A LOS DATA-NODES, EN VEZ DE GUARDARLOS ACÁ
        # USAR HILOS PARA MANDARLOS A LOS DATA-NODES, PORQUE

        file_n = path.split('/')[-1] + '.chunk' + str(chunk)
        # QUE HAYA UN ARRAY CON TODOS LOS CHUNKS, CON TODOS LOS BINARIOS.
        file_t = open('./chunks/' + file_n, 'wb')
        # Y DESPUES QUE CADA HILO MANDA UN CHUNK A UN DATA-NODE
        # Y DESPUES, QUE ESOS HILOS CREEN EL DICCIONARIO CON DONDE MANDARON LOS CHUNKS
        # ESE DATA NODE VA A QUEDAR CON EL CHUNK. Y LUEGO, SE LO DEBE ENVIAR A OTRO DATA NODE QUE TENGA LA REPLICA
        # LUEGO, ESE DATA NODE, LE TIENE QUE DECIR AL CLIENTE DONDE ESTA LA REPLICA

        # EL CLIENTE LE TIENE QUE DECIR AL NAME_NODE A DONDE MANDÓ LOS CHUNKS (QUIZAS LO HACE JUAN XD)
        file_t.write(byte)
        file_t.close()

        byte = file_r.read(chunk_size)

        chunk += 1
    print(f'File hash: {hash.hexdigest()}')
    return hash.hexdigest(), chunks


def rebuild_file(name: str):
    try:
        os.mkdir('./reconstruct')
    except Exception:
        print('./reconstruct/ already exists')

    file_m = open('./reconstruct/' + name, 'wb')
    chunk = 0

    file_name = './chunks/' + name + '.chunk' + str(chunk)
    try:
        file_temp = open(file_name, 'rb')
    except Exception:
        print('not a valid file to reconstruct')
        exit()
    while file_temp:
        print(f'- chunk #{chunk} done')
        byte = file_temp.read()
        file_m.write(byte)

        chunk += 1

        file_name = './chunks/' + name + '.chunk' + str(chunk)
        try:
            file_temp = open(file_name, 'rb')
        except Exception:
            break


def upload_file(user, dfs_path: str, local_path: str):
    file_name = os.path.basename(local_path)
    if dfs_path[-1] != '/':
        dfs_path += '/'
    dfs_path += file_name

    response = command(user, dfs_path, 'can_add')
    message = response.get('message')
    if message != "":
        print(message)
        return
    # se usa para guardar el archivo en el data node
    # username-/path/to/file
    full_path = response.get('full_path')

    print("File will be uploaded to:", full_path)
    # hash, array con los chunks
    hash, chunks = split_file(local_path, CHUNK_SIZE)
    if not hash:
        print('Error when splitting file')
        return

    # available
    # subir los chunks a los data nodes
    # y hacer los mapas con los chunks y las replicas
    # {
    #     'chunk-0': '127.0.0.4',
    #     'chunk-1': '127.0.0.4',
    #     'chunk-2': '127.0.0.4',
    #     'chunk-3': '127.0.0.4',
    # }

    add_file(user, full_path, hash, {}, {})

def download_file(user, dfs_path: str, local_path: str):
    response = command(user, dfs_path, 'file_info')
    message = response.get('message')
    if message != "":
        print(message)
        return

    # usar esto para descargar el archivo
    file_info = response.get('file_info')
    hash = file_info.get('hash')
    chunks = file_info.get('chunks')
    chunksReplicas = file_info.get('chunksReplicas')

    # download chunks

    # rebuild file
    # save file
    # {
    #     'chunk-0': '



def run():
    login_flag = False
    user = ""
    # This print this ascii art
    print("\u001b[32m")
    print("  ____  _____ ____        __  __                     ")
    print(" |  _ \\|  ___/ ___|      |  \\/  | ___  ___ _   _ ___ ")
    print(" | | | | |_  \\___ \\ _____| |\\/| |/ _ \\/ __| | | / __|")
    print(" | |_| |  _|  ___) |_____| |  | |  __/ (__| |_| \\__ \\")
    print(" |____/|_|   |____/      |_|  |_|\\___|\\___|\\__,_|___/")

    curr_dir = ''
    prompt = '\n\u001b[31mPlease login or register to continue\n\u001b[36mType "help" for more information'
    while True:
        print(
            prompt + f'\u001b[33m{curr_dir}')
        user_input = input("\u001b[35m> \u001b[37m")

        args = parse(user_input)
        if not args:
            continue

        if login_flag:
            if args[0] == 'available':
                # AQUÍ VA EL CÓDIGO PARA CONSULTAR LA DISPONIBILIDAD DE LOS DATA-NODES
                # GUARDALOS EN UN ARRAY PARA USARLOS EN EL COMANDO SEND
                available()

            elif args[0] == 'upload':
                if len(args) != 2:
                    print("Usage: upload <file_path_in_dfs>")
                else:
                    print(
                        '\u001b[33mEnter the file path to upload to DFS-Mecus\u001b[36m')
                    path = input('File path (from root): \u001b[37m')
                    upload_file(user, args[1], path)
                    # PONGAN AQUÍ EL CÓDIGO QUE ENVÍE LOS CHUNKS
                    # PARA ENVÍAR EL ARCHIVO :)

                    # ELSE: PRINT("NADA SO, NO SABES A QUIEN MANDARLE LAS VAINAS, HAZ PRIMERO UN "AVAILABLE"")

            elif args[0] == 'download':
                # PONGAN AQUÍ EL CÓDIGO DE ADQUISICIÓN DE LOS CHUNKS
                # PARA REARMAR EL ARCHIVO :)
                print("\nRebuild file")
                file = input('File name: ')
                rebuild_file(file)

            elif args[0] == 'mkdir':
                if len(args) != 2:
                    print("Usage: add_dir <directory_path>")
                else:
                    response = command(user, args[1], 'mkdir')
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

            # Para testear este se usa solo cuando se va a enviar un archivo
            elif args[0] == 'can_add':
                if len(args) != 2:
                    print("Usage: can_add <file_path>")
                else:
                    response = command(user, args[1], 'can_add')
                    message = response.get('message')
                    curr_dir = response.get('curr_dir')
                    full_path = response.get('full_path')
                    if message == "":
                        print("Full file path:", full_path)
                    print(message)

            # Para testear este se usa solo cuando se va a enviar un archivo
            elif args[0] == 'file_info':
                if len(args) != 2:
                    print("Usage: file_info <file_path>")
                else:
                    response = command(user, args[1], 'file_info')
                    message = response.get('message')
                    curr_dir = response.get('curr_dir')
                    file_info = response.get('file_info')
                    print(file_info)
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
                # PONGAN QUE ARGUMENTOS TIENE Y QUE HACE CUANDO LO HAGAN
                print('  available          - Check the availability of the data-nodes')
                print("  cd <path>          - Change directory")
                print('  clear              - Clear the screen')
                print('  download <path>    - IDK')
                print('  help               - Show this help')
                print('  logout             - Stop program')
                print("  ls                 - List directory contents")
                print("  mkdir <path>       - Create a directory")
                # PONGAN QUE ARGUMENTOS TIENE Y QUE HACE CUANDO LO HAGAN
                # PONGAN QUE ARGUMENTOS TIENE Y QUE HACE CUANDO LO HAGAN
                print('  upload <path_in_dfs>       - Upload a file')

            elif args[0] == 'clear':
                os.system('clear')

            else:
                print('Unknown command')

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
            print('Unknown command')


if __name__ == '__main__':
    # prompt to split a file
    run()
