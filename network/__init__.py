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
    PROTO_DELETE = 0x03
    PROTO_ACK = 0x04
    PROTO_JOIN = 0x05
    PROTO_EXIT = 0x06
    PROTO_MOVE = 0x07
    PROTO_REJ = 0x08
    PROTO_LOGIN_CONV = 0x09
    PROTO_LOGIN_COOKIE = 0x0A
    PROTO_LOGIN_FAILED = 0x0B
    PROTO_SUCCESS = 0x0C
    PROTO_FAILED = 0x0D

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
    MSG_INVALID_DATA = 0x10
    MSG_WRONG_CRED = 0x20
    MSG_USER_EXISTS = 0x40
    MSG_USER_NOT_EXIST = 0x50


class LoginOptions(Flag):
    LOGIN_FALSE = 0x00
    LOGIN_TRUE = 0x01
    LOGIN_USERNAME = 0x02
    LOGIN_PASSWORD = 0x03
    LOGIN_COOKIE = 0x04
    LOGIN_ARG = 0x05
    LOGIN_VALUE = 0x06

if __name__ == '__main__':
    print(PROTOCOLS.to_bytes(PROTOCOLS.from_bytes(b'\x1c')))

        