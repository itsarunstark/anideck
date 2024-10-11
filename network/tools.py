from typing import Union, ByteString, Optional, Type, Tuple
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


def decode_msg(x:ByteString, dType:Type)->Tuple[int, Optional[Union[int, str, float, ByteString]]]:
    data_length = from_bytes(x[:2])
    if dType is int:
        return data_length, int.from_bytes(x[2:data_length+2], byteorder='little', signed=False)
    if dType is str:
        return data_length, x[2:data_length+2].decode()
    if dType is float:
        return data_length, struct.unpack("<d", x[2:data_length+2])[0]
    if dType in [bytes, bytearray, ByteString]:
        return data_length, x[2:data_length+2]
    return 0, None
