import requests
import time 
from flask import Flask, request, jsonify
import socket

from bootstrap import *

# Inicialización y configuración de Flask
# Server
app = Flask(__name__)


# Funciones útiles
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
def register_namenode(url, name, ip):
    message = {'name': name, 'ip': ip}
    try:
        response = requests.post(f'{url}/register_dn', json=message)
    except requests.exceptions.RequestException as e:
        print(f"Connection to server failed: {e}")
        exit()

    if response.status_code == 200:
        print('Creation successful!')
    else:
        print('Creation failed.')


def keep_alive():
    while True:
        try:
            response = requests.post(f'{URL}/keep_alive', json={'name': NAME})
            if response.status_code == 200:
                print("keepAlive successful!")
            else:
                print(f"keepAlive failed: {response.json().get('response')}")
        except requests.exceptions.RequestException as e:
            print(f"Connection to server failed: {e}")

        time.sleep(KEEPALVIE_SLEEP_SECONDS)


if __name__ == '__main__':
    register_namenode(URL, NAME, str(get_ip()))
    keep_alive()
