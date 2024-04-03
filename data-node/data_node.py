import requests
import time 
from flask import Flask, request, jsonify

# Inicialización y configuración de Flask
# Server
app = Flask(__name__)

NAMENODE_URL = 'http://127.0.0.1:5000'

def register_with_namenode():
    data = {
        'name': 'data_node_1',  # Replace with the data node's actual name
        'ip': '192.168.1.105'  # Replace with the data node's actual IP address
    }
    response = requests.post(f'{NAMENODE_URL}/registerDn', json=data) 

    if response.status_code == 200:
        print('Registration successful!')
    else:
        print('Registration failed.')

def keepAlive():
    while True:
        try:
            response = requests.get(f'{NAMENODE_URL}/keepAlive')  # Adjust path if needed
            if response.status_code == 200:
                print("keepAlive successful!")
            else:
                print("keepAlive failed.")
        except requests.exceptions.ConnectionError:
            print("Connection to name node lost.")

        time.sleep(5)  # Adjust keepAlive interval as needed



if __name__ == '__main__':
    register_with_namenode()
    keepAlive() 