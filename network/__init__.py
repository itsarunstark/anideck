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
    PROTO_JOIN_BATCH = 0x0E
    PROTO_LEAVE_BATCH = 0x0F
    PROTO_CREATE_BATCH = 0x10
    PROTO_GET_QUEUE_LENGTH = 0x11
    PROTO_QUEUE_WITHDRAW = 0x12

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
    MSG_INTERNAL_ERROR = 0x03
    MSG_BUSY = 0x04
    MSG_INVALID_DATA = 0x05
    MSG_WRONG_CRED = 0x06
    MSG_USER_EXISTS = 0x07
    MSG_USER_NOT_EXIST = 0x08
    MSG_COOKIE_RESPONSE = 0x09
    MSG_LOGIN_FAILED = 0x0A
    MSG_LOGIN_SUCCESS = 0x0B
    MSG_REGISTER_SUCCESS = 0x0C
    MSG_REGISTER_FAILED = 0x0D
    MSG_BATCH_ACTIVITY = 0x0E
    MSG_BATCH_QUEUED = 0x0F
    MSG_QUEUE_LENGTH = 0x10
    MSG_REJECTED = 0x11

    @staticmethod
    def from_bytes(bytedata:bytes):
        return GameMsg(bytedata)
    
    def to_bytes(self):
        return self.value.to_bytes(byteorder='little')


class LoginOptions(Flag):
    LOGIN_FALSE = 0x00
    LOGIN_TRUE = 0x01
    LOGIN_USERNAME = 0x02
    LOGIN_PASSWORD = 0x03
    LOGIN_COOKIE = 0x04
    LOGIN_ARG = 0x05
    LOGIN_VALUE = 0x06

class CookieOpt(Flag):
    COOKIE_START = 0x99
    COOKIE_ID = 0x30
    COOKIE_NAME = 0x31
    COOKIE_VALUE = 0x32
    COOKIE_EXPIRED = 0x33
    COOKIE_CREATED = 0x34
    COOKIE_USER_ID = 0x35
    COOKIE_END = 0x00

    def to_bytes(self)->bytes:
        return self.value.to_bytes(1, byteorder='little')
    
    @classmethod
    def className(self):
        return self.__name__
    
    @staticmethod
    def from_bytes(x:bytes):
        data = int.from_bytes(x, byteorder='little')
        return CookieOpt(data)
    
    def __repr__(self) -> str:
        return self.className()+"::"+self.name
    
if __name__ == '__main__':
    print(PROTOCOLS.to_bytes(PROTOCOLS.from_bytes(b'\x1c')))