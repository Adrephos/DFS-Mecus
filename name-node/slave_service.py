import NameNode_pb2_grpc
import NameNode_pb2
from tinydb import TinyDB
from bootstrap import KEEPALIVE_SLEEP_SECONDS
from datetime import datetime, timedelta


class DBService(NameNode_pb2_grpc.DBServiceServicer):
    def __init__(self, db: TinyDB):
        self.send_db = False
        self.last_heartbeat = datetime.now()

    def UploadDB(self, request, context):
        try:
            file = open('db.json', 'wb')
            file.write(request.db)
            file.close()
            self.db.clear_cache()
            return NameNode_pb2.UploadDBResponse(
                status='ok',
                message='DB uploaded successfully')
        except Exception:
            return NameNode_pb2.UploadDBResponse(
                status='not ok',
                message='Error creating db')

    def HeartBeat(self, request, context):
        self.last_heartbeat = datetime.now()
        print(f'Heartbeat received from {request.ip}:{request.port}')
        return NameNode_pb2.HeartBeatResponse(
            status='ok',
            message='Heartbeat received')

    def DownloadDB(self, request, context):
        now = datetime.now()
        threshold = now - timedelta(seconds=KEEPALIVE_SLEEP_SECONDS * 2)

        if self.last_heartbeat > threshold:
            return NameNode_pb2.DownloadDBResponse(
                canDownload=False,
                db=b'')
        try:
            file = open('db.json', 'rb')
            return NameNode_pb2.DownloadDBResponse(
                canDownload=True,
                db=file.read())
        except Exception:
            return NameNode_pb2.DownloadDBResponse(
                canDownload=False,
                db=b'')
