import requests
import time
from flask import Flask, request, jsonify
import socket
    
import grpc
from file_transfer_pb2 import FileChunk
from file_transfer_pb2 import ChunkRequest
from file_transfer_pb2_grpc import FileTransferServiceStub, FileTransferServiceServicer, add_FileTransferServiceServicer_to_server


import threading
from concurrent import futures

from bootstrap import URL, NAME, KEEPALIVE_SLEEP_SECONDS

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

        time.sleep(KEEPALIVE_SLEEP_SECONDS)

class data_service_to_client(FileTransferServiceServicer):

    def get_chunk(self, request, context):
        chunk_id = 69420
        print(f"Received request for chunk {chunk_id}")
        return ("Hello World, chunk_id: " + str(chunk_id))

def serve_upload_to_client():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  
    add_FileTransferServiceServicer_to_server(data_service_to_client(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    register_namenode(URL, NAME, str(get_ip()))
    keep_alive()

    grpc_thread = threading.Thread(target=serve_upload_to_client)
    grpc_thread.start()
