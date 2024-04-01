import os
import requests
import socket

from boostrap import *


# Funciones utiles
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


# Funciones de Flask
def register_login(url, name, password, ip):
    mensaje = {'name': name, 'password': password, 'ip': ip}
    response = requests.post(url, json=mensaje)

    if response.status_code == 200:
        print('Response from server:', response.json().get('response'))
        return response.json().get('response')
    else:
        print('Error when connecting to server')


# Funciones propias del cliente
def split_file(path: str, chunk_size: int):
    file_r = open(path, "rb")
    chunk = 0
    byte = file_r.read(chunk_size)

    try:
        os.mkdir('./chunks')
    except:
        print('./chunks/ already exists')

    while byte:
        file_n = path.split('/')[-1] + '.chunk' + str(chunk)
        file_t = open('./chunks/' + file_n, 'wb')
        file_t.write(byte)
        file_t.close()

        byte = file_r.read(chunk_size)

        chunk += 1


def rebuild_file(name: str):
    try:
        os.mkdir('./reconstruct')
    except:
        print('./reconstruct/ already exists')

    file_m = open('./reconstruct/' + name, 'wb')
    chunk = 0

    file_name = './chunks/' + name + '.chunk' + str(chunk)
    try:
        file_temp = open(file_name, 'rb')
    except:
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
        except:
            break


def run():
    login_flag = False
    while True:
        user_input = input()
        args = parse(user_input)

        if login_flag:
            if args[0] == 'available':
                # AQUÍ VA EL CÓDIGO PARA CONSULTAR LA DISPONIBILIDAD DE LOS DATA-NODES
                # GUARDALOS EN UN ARRAY PARA USARLOS EN EL COMANDO SEND
                pass

            elif args[0] == 'send':
                # IF ARRAY:
                print('Split file')
                file = input('File path (from root): ')
                split_file(file, CHUNK_SIZE)
                # PONGAN AQUÍ EL CÓDIGO QUE ENVÍE LOS CHUNKS
                # PARA ENVÍAR EL ARCHIVO :)

                # ELSE: PRINT("NADA SO, NO SABES A QUIEN MANDARLE LAS VAINAS, HAZ PRIMERO UN "AVAILABLE"")

            elif args[0] == 'read':
                # PONGAN AQUÍ EL CÓDIGO DE ADQUISICIÓN DE LOS CHUNKS
                # PARA REARMAR EL ARCHIVO :)
                print("\nRebuild file")
                file = input('File name: ')
                rebuild_file(file)

            elif args[0] == 'logout':
                print("Ending program...")
                break

            elif args[0] == 'help' and len(args) == 1:
                print('available commands:')
                print('  available          - IDK')  # PONGAN QUE ARGUMENTOS TIENE Y QUE HACE CUANDO LO HAGAN
                print('  help               - Show this help')
                print('  logout             - Stop program')
                print('  read               - IDK')  # PONGAN QUE ARGUMENTOS TIENE Y QUE HACE CUANDO LO HAGAN
                print('  send               - IDK')  # PONGAN QUE ARGUMENTOS TIENE Y QUE HACE CUANDO LO HAGAN

            else:
                print('Unknown command')

        elif args[0] == 'login' and len(args) == 3:
            login = register_login(f"{URL}/login", args[1], args[2], str(get_ip()))
            if login == 'Successful login':
                login_flag = True
                print(f'Welcome {args[1]}')

        elif args[0] == 'register' and len(args) == 3:
            register = register_login(f"{URL}/register", args[1], args[2], str(get_ip()))
            if register == 'Successful registration':
                login_flag = True
                print(f'Welcome {args[1]}')

        elif args[0] == 'help' and len(args) == 1:
            print('available commands:')
            print('  help               - Show this help')
            print('  login <name> <password> - Just a simple login')
            print('  register <name> <password> - Just a simple register')

        else:
            print('Unknown command')


if __name__ == '__main__':
    run()
