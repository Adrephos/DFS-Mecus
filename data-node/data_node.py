import os
import threading
import requests
import time
from flask import Flask
import socket
from concurrent import futures

import grpc
from file_transfer_pb2 import UploadStatus
from file_transfer_pb2_grpc import FileTransferServiceServicer, add_FileTransferServiceServicer_to_server

from bootstrap import URL, NAME, KEEPALIVE_SLEEP_SECONDS, PORT, MY_IP

# Inicialización y configuración de Flask
# Server
app = Flask(__name__)


# Funciones de Flask
def register_namenode(url, name, data_node_url):
    message = {'name': name, 'ip': data_node_url}
    try:
        response = requests.post(f'{url}/register_dn', json=message)
    except requests.exceptions.RequestException as e:
        print(f"Connection to server failed: {e}")
        exit()

    if response.status_code == 200:
        print('Creation successful!')
    else:
        print('Creation failed.')


# Keep-alive thread
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


# gRPC DataNodeService
class DataNodeService(FileTransferServiceServicer):
    def Upload(self, request, context):
        try:
            os.makedirs('./chunks', exist_ok=True)
            with open(f"./chunks/{request.filename}.chunk{request.chunk_id}", "wb") as file:
                file.write(request.data)
                print(
                    f"Chunk {request.chunk_id} de {request.filename} recibido.")
            return UploadStatus(success=True, message="Chunk recibido exitosamente.")
        except Exception as e:
            return UploadStatus(success=False, message=str(e))


# gRPC Server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_FileTransferServiceServicer_to_server(DataNodeService(), server)
    server.add_insecure_port('0.0.0.0:' + str(PORT))
    server.start()
    print("Data Node gRPC Server running...")
    server.wait_for_termination()


if __name__ == '__main__':
    # Registro en el NameNode
    register_namenode(URL, NAME, f'{MY_IP}:{PORT}')

    # Inicia el hilo de gRPC Server
    grpc_thread = threading.Thread(target=serve)
    grpc_thread.start()

    keep_alive()
