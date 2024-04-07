from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FileChunk(_message.Message):
    __slots__ = ("filename", "chunk_id", "data", "hash")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    CHUNK_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    filename: str
    chunk_id: int
    data: bytes
    hash: str
    def __init__(self, filename: _Optional[str] = ..., chunk_id: _Optional[int] = ..., data: _Optional[bytes] = ..., hash: _Optional[str] = ...) -> None: ...

class UploadStatus(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

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

class ChunkRequest(_message.Message):
    __slots__ = ("chunk_name",)
    CHUNK_NAME_FIELD_NUMBER: _ClassVar[int]
    chunk_name: str
    def __init__(self, chunk_name: _Optional[str] = ...) -> None: ...

class ChunkRespond(_message.Message):
    __slots__ = ("chunk_respond",)
    CHUNK_RESPOND_FIELD_NUMBER: _ClassVar[int]
    chunk_respond: str
    def __init__(self, chunk_respond: _Optional[str] = ...) -> None: ...

class ChunkData(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...
