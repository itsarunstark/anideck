from enum import Enum, Flag
from typing import Union
import struct

#protocols to define
#Login
#register
#delete

class PROTOCOLS(Flag):
    PROTO_NONE = 0x00
    PROTO_LOGIN = 0x01
    PROTO_REGISTER = 0x02
    PROTO_DELETE = 0x04
    PROTO_ACK = 0x08
    PROTO_JOIN = 0x10
    PROTO_EXIT = 0x20
    PROTO_MOVE = 0x40
    PROTO_REJ = 0x80

    @staticmethod
    def from_bytes(byte:Union[bytes,bytearray]):
        singlebyte = byte[0]
        return PROTOCOLS(singlebyte)
    
    @staticmethod
    def to_bytes(proto)->bytes:
        return int.to_bytes(proto.value, length=1, byteorder='little', signed=False)

class GameMsg(Flag):
    MSG_BAD_FORMAT = 0x01
    MSG_OK = 0x02
    MSG_INTERNAL_ERROR = 0x04
    MSG_BUSY = 0x08

if __name__ == '__main__':
    print(PROTOCOLS.to_bytes(PROTOCOLS.from_bytes(b'\x1c')))

        