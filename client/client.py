import os
import requests
from boostrap import *


# Funciones utiles
def parse(message: str):
    parse_message = message.split()

    return parse_message


# Funciones de Flask
def register(url, name, password):
    mensaje = {"name": name, "password": password}
    response = requests.post(url, json=mensaje)

    if response.status_code == 200:
        print(f"Response from server:", response.json().get('response'))
    else:
        print("Error when connecting to server")


# Funciones propias del cliente
def split_file(path: str, chunk_size: int):
    file_r = open(path, "rb")
    chunk = 0
    byte = file_r.read(chunk_size)

    try:
        os.mkdir("./chunks")
    except:
        print("./chunks/ already exists")

    while byte:
        file_n = path.split("/")[-1] + ".chunk" + str(chunk)
        file_t = open("./chunks/" + file_n, "wb")
        file_t.write(byte)
        file_t.close()

        byte = file_r.read(chunk_size)

        chunk += 1


def rebuild_file(name: str):
    try:
        os.mkdir("./reconstruct")
    except:
        print("./reconstruct/ already exists")

    file_m = open("./reconstruct/" + name, "wb")
    chunk = 0

    file_name = "./chunks/" + name + ".chunk" + str(chunk)
    try:
        file_temp = open(file_name, "rb")
    except:
        print("not a valid file to reconstruct")
        exit()
    while file_temp:
        print(f'- chunk #{chunk} done')
        byte = file_temp.read()
        file_m.write(byte)

        chunk += 1

        file_name = "./chunks/" + name + ".chunk" + str(chunk)
        try:
            file_temp = open(file_name, "rb")
        except:
            break


def run():
    while BANDERA:
        user_input = input()
        parse_input = parse(user_input)

        if parse_input[0] == "register" and len(parse_input) == 3:
            register(URL, parse_input[1], parse_input[2])

        elif parse_input[0] == "send":
            print("Split file")
            file = input("File path (from root): ")
            split_file(file, 1400*1024)

        elif parse_input[0] == "read":
            # PONGAN AQUÍ EL CÓDIGO DE ADQUISICIÓN DE LOS CHUNKS
            # PARA REARMAR EL ARCHIVO :)
            print("\nRebuild file")
            file = input("File name: ")
            rebuild_file(file)
        else:
            print("Unknown command")


if __name__ == '__main__':
    run()
