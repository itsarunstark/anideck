import socket
import select
import logging
import time
from typing import Union, List, Set, Tuple
import os
from network import PROTOCOLS, GameMsg
import uuid
import struct
import sqlite3

to_bytes = lambda x:x.to_bytes(length=2, byteorder='little', signed=False)
from_bytes = lambda x:int.from_bytes(x, byteorder='little', signed=False)


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
        try:
            data = sock.recv(1)
        except (ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError) as e:
            logger.error(e.strerror)
            data = b''
        if not len(data):
            if sock in self.queued_connections: del self.queued_connections[sock]
            if sock in self.pooling_socks: self.pooling_socks.remove(sock)
            logger.info("lost connection:: [{}]".format(sock.fileno()))
            sock.close()
            return
        
        proto = PROTOCOLS.from_bytes(data)
        if sock in self.queued_connections:
            
            if (proto&PROTOCOLS.PROTO_ACK):
                logger.info("Connection verified timelimit::%0.4f", time.time() - self.queued_connections[sock])
                sock.send(PROTOCOLS.to_bytes(PROTOCOLS.PROTO_ACK))
                del self.queued_connections[sock]
        
        elif (proto & PROTOCOLS.PROTO_REGISTER):
            msg,valid = self.recv_bytes(sock)
            print("message::", msg)
            if valid: self.register_function(self, sock, msg)
    
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
        try:
            lengthpack = sock.recv(2)
        except:
            lengthpack = b'\x00\x00'
        logger.debug("lengthpacket::%a"%lengthpack)
        datalength = int.from_bytes(lengthpack, byteorder='little', signed=False)
        logger.debug("DATALENGTH TO ACCEPT:%d"%datalength)
        protodata = bytearray(datalength)
        dt = 0
        data_incoming = True
        tries = 3
        
        while(dt<datalength and data_incoming):
            try:
                incomedata = sock.recv(self.chunks)
            except BlockingIOError:
                incomedata = b''
            dLength = len(incomedata)
            if (not dLength):
                if (tries>0):
                    tries -= 1
                else:
                    logger.warn("recieved invalid datpacked :: decision :: dropping data")
                    protodata.zfill(datalength)
                    dt = 0
                    data_incoming = False
            protodata[dt:dt+dLength] = incomedata
            dt += dLength
            logger.info("data_ack:%d"%data_incoming)
        sock.send(
            PROTOCOLS.to_bytes(
                PROTOCOLS.PROTO_ACK if data_incoming else PROTOCOLS.PROTO_REJ 
            )
        )
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
        """
        @params proto:PROTOCOL
        @params msg:Union[str,bytes,bytearray]
        @return encoded data , length of data 
        """
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
            return
        valid,data = self.extract_auth(msg)
        if (not valid):
            server.senddata(
                sock, *self.encode_game_msg(GameMsg.MSG_INVALID_DATA, "Invalid Data is recived auth Faild")
            )
            return
        logger.info("username:%s pass:%s"%data)
        try:

            self.cursor.execute("SELECT userId FROM Users WHERE userName=? AND userPass=?", (data[0], data[1].hex()))
            logger.debug("finished till here")
            crossdata = self.cursor.fetchall()
            if (len(crossdata)):
                server.senddata(
                    sock, *self.encode_game_msg(GameMsg.MSG_USER_EXISTS, "User Exists")
                )
                return
            userid = from_bytes(struct.pack("<d", time.time_ns()))
            logger.debug("current id %d"%userid)
            self.cursor.execute(
                "INSERT INTO Users(userId, userName, userPass) values(?, ?, ?)",
                (userid, data[0], data[1].hex())
            )
            self.database.commit()
            server.senddata(
                sock, *self.encode_game_msg(GameMsg.MSG_OK, "REQUEST_ACCEPTED")
            )
        except Exception as serverError:
            error = server.encode_msg(PROTOCOLS.PROTO_REJ, str(serverError))
            logger.error(error[0])
            server.senddata(
                sock, *error
            )


    def extract_auth(self, bytearr:Union[bytes,bytearray])->Tuple[bool, Tuple[str,Union[bytes,bytearray]]]:
        """
        @params bytearr : array bytes
        @return Tuple[bool, Tuple[str, str]] if valid auth, username, password
        """
        userlength = int.from_bytes(bytearr[:2], byteorder='little', signed=False)
        passlength = int.from_bytes(bytearr[2+userlength:4+userlength], byteorder='little', signed=False)
        username = bytearr[2:2+userlength].decode()
        userpass = bytearr[4+userlength:4+userlength+passlength]
        if (not ((userlength and passlength) and len(username) and len(userpass))):
            return False,(username, userpass)
        return True, (username, userpass)

    
    def encode_game_msg(self,msgProto:GameMsg, data:Union[bytes,str,bytearray])->Tuple[bytes,int]:
        # if isinstance()
        dData = data if (isinstance(data, bytes) or isinstance(data,bytearray)) else data.encode()
        proto = PROTOCOLS.to_bytes(msgProto)
        # dLenght = 
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