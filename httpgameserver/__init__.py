import socket
import select
import logging
import time
from typing import Union, List, Set, Tuple
import os
from network import PROTOCOLS, GameMsg


import sqlite3



class ColorFormatter(logging.Formatter):
    red = '\x1b[31;3m'
    green = '\x1b[32;3m'
    yellow = '\x1b[33;3m'
    redHigh = '\x1b[31;3m'
    blue = '\x1b[35;3m'
    redBack = '\x1b[41;3m'
    reset = '\x1b[0m'
    loggerFormat = "%(asctime)s:%(name)s:%(levelname)s::%(message)s (%(filename)s:%(lineno)d)"
    COLORS = {
        logging.DEBUG : blue + loggerFormat + reset, 
        logging.WARNING : yellow + loggerFormat + reset,
        logging.ERROR : red + loggerFormat + reset,
        logging.CRITICAL : redHigh + loggerFormat + reset,
        logging.FATAL : redBack + loggerFormat + reset,
        logging.INFO : green + loggerFormat + reset
    }
    def format(self, record):
        log_fmt = self.COLORS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    

logger = logging.getLogger('Game Server')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logger.level)
handler.setFormatter(ColorFormatter())
logger.addHandler(handler)

USERDB = "./userlogin.db"
ACTIVEDB = "./activeplayers.db"

class Connection:
    def __init__(self, connectionId, sock:socket.socket):
        self.socket:socket.socket = sock
        self.runtimedata = {}
    
    def read_updates(self):
        print("read request detected")

class User(object):
    def __init__(self, userId, username, connection:socket.socket=None):
        self.userId = userId
        self.username = username
        self.connection:socket.socket = connection

    def read_msg(self):
        logger.warning("Not yet implemented")


    
class Sever:
    def __init__(self,addr:Union[str,bytes], port:int=65432):
        self.addr:Union[str,bytes] = addr
        self.port:int = port
        self.queued:int = 10
        self.socket:socket.socket = socket.socket()
        self.listening:bool = False
        self.socket_configure_default_options()
        self.pooling_socks:Set[socket.socket] = set()
        self.queued_connections = {}
        self.verified_connections = {}
        self.chunks = 1024
        self.register_function = lambda server,sock,msg:print(msg)

    
    def socket_configure_default_options(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.socket.setblocking(False)
        if os.name == 'posix' : 
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)


    def bind_port(self):
        self.socket.bind((self.addr, self.port))
        self.pooling_socks.add(self.socket)
        self.listening = True
        logger.info("binded port successfully.")
    
    def listen_port(self):
        self.socket.listen(self.queued)
    
    def __del__(self):
        logger.debug("Closing socket object::[{}:{}]".format(self.addr, self.port))
        if (self.listening):
            self.socket.close()
    
    def accept_connection(self, socket:socket.socket):
        sock,addr = socket.accept()
        logger.info("client queued::%s"%addr[0])
        self.queued_connections[sock] = time.time()
        self.pooling_socks.add(sock)
    
    def read_bytes(self,sock:socket.socket):
        data = sock.recv(1)
        if not len(data):
            if sock in self.queued_connections:
                del self.queued_connections[sock]

            if sock in self.pooling_socks:
                self.pooling_socks.remove(sock)
            logger.info("lost connection:: [{}]".format(sock.fileno()))
            sock.close()
            return
        
        if sock in self.queued_connections:
            # time.sleep(1)
            msg = data
            proto = PROTOCOLS.from_bytes(msg)
            if (PROTOCOLS.PROTO_ACK&proto):
                logger.info("Connection verified timelimit::%0.4f", time.time() - self.queued_connections[sock])
                del self.queued_connections[sock]
        
        PROTOCOL = PROTOCOLS.from_bytes(data)
        if (PROTOCOL & PROTOCOLS.PROTO_REGISTER):
            msg,valid = self.recv_bytes(sock)
            print("message::", msg)
            if not valid:
                msg,length = self.encode_msg(PROTOCOLS.PROTO_REJ, "datapacked length mismatched please try again")
                self.senddata(sock, msg, length)
            else:
                msg,length = self.encode_msg(PROTOCOLS.PROTO_ACK, "data accepted, thankyou")
                self.register_function(self, sock, msg)
    
    def senddata(self,sock:socket.socket, msg:Union[bytes,bytearray], length):
        sentLength = 0
        while(sentLength<length):
            chunkmsg = msg[sentLength:sentLength+self.chunks]
            if (not len(chunkmsg)):return sentLength
            sentLength += sock.send(
                chunkmsg
            )
        return sentLength


    
    def recv_bytes(self,sock)->Tuple[bytearray, bool]:
        lengthpack = sock.recv(2)
        datalength = int.from_bytes(lengthpack, byteorder='little', signed=False)
        logger.debug("DATALENGTH TO ACCEPT:%d"%datalength)
        protodata = bytearray(datalength)
        dt = 0
        data_incoming = True
        tries = 3
        
        while(dt<datalength and data_incoming):
            incomedata = sock.recv(self.chunks)
            dLength = len(incomedata)
            if (not dLength):
                if (tries>0):
                    tries -= 1
                else:
                    logger.warn("recieved invalid datpacked :: decision :: dropping data")
                    protodata.zfill(datalength)
                    dt = 0
                    data_incoming = False
                    return protodata
            protodata[dt:dt+dLength] = incomedata
            dt += dLength
        return (protodata, data_incoming)


    def pool(self):
        readables, writables, exceptables = select.select(self.pooling_socks, [], [], 0)
        # logger.info(readables)
        for readable in readables:
            if readable is self.socket:
                self.accept_connection(readable)
            else:
                self.read_bytes(readable)
    
    def encode_msg(self, proto:PROTOCOLS, msg:Union[str,bytes,bytearray])->Tuple[bytes,int]:
        protocolbyte = PROTOCOLS.to_bytes(proto)
        enc = msg if (isinstance(msg, bytes) or isinstance(msg,bytearray)) else msg.encode()
        dLength = len(enc)
        dLd = dLength.to_bytes(2, byteorder='little', signed=False)
        print(enc, dLd, protocolbyte)
        return protocolbyte+dLd+enc, 3 + dLength

    
    def remove_queued(self,sock:socket.socket)->None:
        del self.queued_connections[sock]
        self.pooling_socks.remove(sock)



class GameServer:
    def __init__(self, server):
        self.userdatabase = "sakshi.db"
        self.database = sqlite3.connect(self.userdatabase)
        self.cursor = self.database.cursor()
        self.server = server
        self.server.register_function = self.register_user
    def register_user(self,server:Sever,sock:socket.socket,msg:bytearray):
        if (len(msg) < 10):
            server.senddata(
                sock, *self.encode_game_msg(GameMsg.MSG_BAD_FORMAT, "Bad Format Failed")
            )
        else:
            server.senddata(
                sock, *self.encode_game_msg(GameMsg.MSG_OK, "REQUEST_ACCEPTED")
            )
    
    def encode_game_msg(self,msgProto:GameMsg, data:Union[bytes,str,bytearray])->Tuple[bytes,int]:
        # if isinstance()
        dData = data if (isinstance(data, bytes) or isinstance(data,bytearray)) else data.encode()
        proto = PROTOCOLS.to_bytes(msgProto)
        return server.encode_msg(PROTOCOLS.PROTO_ACK, proto+dData)
        # self.database = 




VERIFICATION_TIMEOUT = 0.500
server = Sever('127.0.0.1', 65432)
server.bind_port()
server.listen_port()
to_remove:Set[socket.socket] = set()
game= GameServer(server)
while True: 
    t0 = time.time()
    server.pool()
    to_remove.clear()
    for sock,limit in server.queued_connections.items():
        if (t0-limit > VERIFICATION_TIMEOUT):
            to_remove.add(sock)
    for sock in to_remove:
        server.remove_queued(sock)
        logger.warn("The end for {}".format(sock))