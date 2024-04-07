import os
import threading
import requests
import time
from flask import Flask, request, jsonify
import socket
from concurrent import futures

import grpc

from file_transfer_pb2 import UploadStatus
from file_transfer_pb2_grpc import FileTransferServiceServicer, add_FileTransferServiceServicer_to_server

from file_transfer_pb2 import FileChunk
from file_transfer_pb2 import ChunkRequest
from file_transfer_pb2_grpc import FileTransferServiceStub, FileTransferServiceServicer, add_FileTransferServiceServicer_to_server

import threading



from bootstrap import URL, NAME, KEEPALIVE_SLEEP_SECONDS, PORT

# Inicialización y configuración de Flask
# Server
app = Flask(__name__)


# Util functions
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

# gRPC DataNodeService
class DataNodeService(FileTransferServiceServicer):
    def Upload(self, request, context):
        try:
            os.makedirs('./chunks', exist_ok=True)
            with open(f"./chunks/{request.filename}_{request.chunk_id}.chunk", "wb") as file:
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
    register_namenode(URL, NAME, f'{get_ip()}:{PORT}')

    # Inicia el hilo de gRPC Server
    grpc_thread = threading.Thread(target=serve)
    grpc_thread.start()

    keep_alive()

    grpc_thread = threading.Thread(target=serve_upload_to_client)
    grpc_thread.start()
