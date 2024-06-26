from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FileChunk(_message.Message):
    __slots__ = ("filename", "chunk_id", "data", "replicate", "hash")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    CHUNK_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    REPLICATE_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    filename: str
    chunk_id: int
    data: bytes
    replicate: bool
    hash: str
    def __init__(self, filename: _Optional[str] = ..., chunk_id: _Optional[int] = ..., data: _Optional[bytes] = ..., replicate: bool = ..., hash: _Optional[str] = ...) -> None: ...

class UploadStatus(_message.Message):
    __slots__ = ("success", "replica_url", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    REPLICA_URL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    replica_url: str
    message: str
    def __init__(self, success: bool = ..., replica_url: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class FileDownloadRequest(_message.Message):
    __slots__ = ("filename",)
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    filename: str
    def __init__(self, filename: _Optional[str] = ...) -> None: ...

class FileDownloadResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...
