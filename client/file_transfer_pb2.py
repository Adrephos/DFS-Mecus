# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: file_transfer.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13\x66ile_transfer.proto\x12\x0c\x66iletransfer\"K\n\tFileChunk\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x10\n\x08\x63hunk_id\x18\x02 \x01(\x05\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c\x12\x0c\n\x04hash\x18\x04 \x01(\t\"0\n\x0cUploadStatus\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"\'\n\x13\x46ileDownloadRequest\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\"$\n\x14\x46ileDownloadResponse\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\"\"\n\x0c\x43hunkRequest\x12\x12\n\nchunk_name\x18\x01 \x01(\t\"%\n\x0c\x43hunkRespond\x12\x15\n\rchunk_respond\x18\x01 \x01(\t\"\x19\n\tChunkData\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\x32\xf3\x01\n\x13\x46ileTransferService\x12?\n\x06Upload\x12\x17.filetransfer.FileChunk\x1a\x1a.filetransfer.UploadStatus\"\x00\x12U\n\x08\x44ownload\x12!.filetransfer.FileDownloadRequest\x1a\".filetransfer.FileDownloadResponse\"\x00\x30\x01\x12\x44\n\x08GetChunk\x12\x1a.filetransfer.ChunkRequest\x1a\x1a.filetransfer.ChunkRespond\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'file_transfer_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_FILECHUNK']._serialized_start=37
  _globals['_FILECHUNK']._serialized_end=112
  _globals['_UPLOADSTATUS']._serialized_start=114
  _globals['_UPLOADSTATUS']._serialized_end=162
  _globals['_FILEDOWNLOADREQUEST']._serialized_start=164
  _globals['_FILEDOWNLOADREQUEST']._serialized_end=203
  _globals['_FILEDOWNLOADRESPONSE']._serialized_start=205
  _globals['_FILEDOWNLOADRESPONSE']._serialized_end=241
  _globals['_CHUNKREQUEST']._serialized_start=243
  _globals['_CHUNKREQUEST']._serialized_end=277
  _globals['_CHUNKRESPOND']._serialized_start=279
  _globals['_CHUNKRESPOND']._serialized_end=316
  _globals['_CHUNKDATA']._serialized_start=318
  _globals['_CHUNKDATA']._serialized_end=343
  _globals['_FILETRANSFERSERVICE']._serialized_start=346
  _globals['_FILETRANSFERSERVICE']._serialized_end=589
# @@protoc_insertion_point(module_scope)