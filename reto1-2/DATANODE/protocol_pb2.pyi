from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ReplicateChunkRequest(_message.Message):
    __slots__ = ("chunk_id", "chunk_content")
    CHUNK_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_CONTENT_FIELD_NUMBER: _ClassVar[int]
    chunk_id: str
    chunk_content: bytes
    def __init__(self, chunk_id: _Optional[str] = ..., chunk_content: _Optional[bytes] = ...) -> None: ...

class ReplicateChunkResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ListFilesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListFilesResponse(_message.Message):
    __slots__ = ("file_names",)
    FILE_NAMES_FIELD_NUMBER: _ClassVar[int]
    file_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, file_names: _Optional[_Iterable[str]] = ...) -> None: ...
