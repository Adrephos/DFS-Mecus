from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UploadDBRequest(_message.Message):
    __slots__ = ("db",)
    DB_FIELD_NUMBER: _ClassVar[int]
    db: bytes
    def __init__(self, db: _Optional[bytes] = ...) -> None: ...

class UploadDBResponse(_message.Message):
    __slots__ = ("status", "message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: str
    message: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class HeartBeatRequest(_message.Message):
    __slots__ = ("name", "ip", "port")
    NAME_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    name: str
    ip: str
    port: int
    def __init__(self, name: _Optional[str] = ..., ip: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...

class HeartBeatResponse(_message.Message):
    __slots__ = ("status", "message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: str
    message: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class DownloadDBRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class DownloadDBResponse(_message.Message):
    __slots__ = ("canDownload", "db")
    CANDOWNLOAD_FIELD_NUMBER: _ClassVar[int]
    DB_FIELD_NUMBER: _ClassVar[int]
    canDownload: bool
    db: bytes
    def __init__(self, canDownload: bool = ..., db: _Optional[bytes] = ...) -> None: ...
