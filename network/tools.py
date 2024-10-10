from typing import Union, ByteString
import struct

to_bytes = lambda x:x.to_bytes(length=2, byteorder='little', signed=False)
from_bytes = lambda x:int.from_bytes(x, byteorder='little', signed=False)

def encode_msg(x:Union[bytes, str, int, float, bytearray])->ByteString:
    if (isinstance(x, str)):
        encoded_string = x.encode()
        return to_bytes(len(encoded_string)) + encoded_string
    if (isinstance(x, int)):
        encoded_int = x.to_bytes(8, byteorder='little', signed=False)
        return to_bytes(len(encoded_int)) + encoded_int
    if (isinstance(x, bytes) or isinstance(x, bytearray)):
        return to_bytes(len(x)) + x
    if (isinstance(x, float)):
        encoded_float = struct.pack("<d", x)
        return to_bytes(len(encoded_float)) + encoded_float
    return b''
