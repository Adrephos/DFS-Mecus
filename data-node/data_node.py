import os
import threading
import requests
import time
import random
from flask import Flask
from concurrent import futures

import grpc
from file_transfer_pb2_grpc import FileTransferServiceServicer, add_FileTransferServiceServicer_to_server, FileTransferServiceStub
from file_transfer_pb2 import UploadStatus, FileChunk, FileDownloadRequest, FileDownloadResponse

from bootstrap import URL, URL_SLAVE, NAME, KEEPALIVE_SLEEP_SECONDS, MY_IP, PORT

# Flask initialization and configuration
# Server
app = Flask(__name__)


# Flask functions
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
        except requests.exceptions.RequestException:
            try:
                register_namenode(URL_SLAVE, NAME, f'{MY_IP}:{PORT}')
                response = requests.post(
                    f'{URL_SLAVE}/keep_alive', json={'name': NAME})
            except requests.exceptions.RequestException as e:
                print(f"Connection to server failed: {e}")

        if response.status_code == 200:
            print("keepAlive successful!")
        else:
            print(f"keepAlive failed: {response.json().get('response')}")

        time.sleep(KEEPALIVE_SLEEP_SECONDS)


def get_data_nodes():
    try:
        response = requests.post(f'{URL}/available')
    except requests.exceptions.ConnectionError:
        try:
            response = requests.post(f'{URL_SLAVE}/available')
        except requests.exceptions.ConnectionError as e:
            print(f"Connection to server failed: {e}")
            return []
    if response.status_code == 200:
        return response.json()
    else:
        print(f"get_data_nodes failed: {response.json().get('response')}")
        return []


# remove this node from datanodes array
def remove_self(data_nodes):
    new_data_nodes = []
    for data_node in data_nodes:
        if data_node['ip'] != f'{MY_IP}:{PORT}':
            new_data_nodes.append(data_node)
    return new_data_nodes


# gRPC DataNodeService
def replicate_chunk(data_node, request):
    try:
        with grpc.insecure_channel(data_node) as channel:
            stub = FileTransferServiceStub(channel)
            response = stub.Upload(
                FileChunk(
                    filename=request.filename,
                    chunk_id=request.chunk_id,
                    data=request.data,
                    replicate=False,
                    hash=request.hash
                ))
            print(
                f"Chunk {request.chunk_id} from {request.filename} replicated in {request.data_node}")
            return response
    except Exception as e:
        print(f"Error replicating chunk: {e}")
        return UploadStatus(success=False, message=str(e))


class DataNodeService(FileTransferServiceServicer):
    def Upload(self, request, context):
        try:
            os.makedirs('./chunks', exist_ok=True)
            with open(f"./chunks/{request.filename}.chunk{request.chunk_id}", "wb") as file:
                file.write(request.data)
                print(
                    f"Chunk {request.chunk_id} from {request.filename} received")
            # replicate chunk in other data node
            replica_url = ""
            try:
                data_nodes = remove_self(get_data_nodes())
                data_node = random.choice(data_nodes)
                if request.replicate and len(data_nodes) > 0:
                    replicate_chunk(data_node['ip'], request)
                replica_url = data_node['ip']
            except Exception as e:
                print(f"Error replicating chunk: {e}")
            return UploadStatus(success=True, replica_url=replica_url, message="Chunk received successfully")
        except Exception as e:
            return UploadStatus(success=False, message=str(e))

    def Download(self, request: FileDownloadRequest, context):
        chunk_path = f"./chunks/{request.filename}"
        if not os.path.exists(chunk_path):
            context.abort(grpc.StatusCode.NOT_FOUND, "Chunk not found")
        with open(chunk_path, 'rb') as chunk_file:
            chunk_data = chunk_file.read()
        print(f"Sent chunk from {request.filename}")
        return FileDownloadResponse(data=chunk_data)


# gRPC Server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_FileTransferServiceServicer_to_server(DataNodeService(), server)
    server.add_insecure_port('0.0.0.0:' + str(PORT))
    server.start()
    print("Data Node gRPC Server running...")
    server.wait_for_termination()


if __name__ == '__main__':
    register_namenode(URL, NAME, f'{MY_IP}:{PORT}')

    grpc_thread = threading.Thread(target=serve)
    grpc_thread.start()

    keep_alive()
