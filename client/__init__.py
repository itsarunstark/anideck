import socket
from typing import Tuple, List, Set, Union, Callable, Optional
from network import PROTOCOLS, GameMsg, CookieOpt
from network.tools import to_bytes, from_bytes, encode_msg, decode_msg
from network.cookiejar import Cookie, CookieManager
import hashlib
import sqlite3
import os
import sys
import time
import struct

to_bytes:Callable = lambda x:x.to_bytes(length=2, byteorder='little', signed=False)
from_bytes:Callable = lambda x:int.from_bytes(x, byteorder='little', signed=False)


class Client:
    def __init__(self, addr,port):
        self.addr:str = addr
        self.port:int = port
        self.clientsock:socket.socket = None
        self.verified = False
        self.chunks = 1024

    def ack_server(self)->bool:
        if not (self.clientsock) :
            raise ValueError("socket value is {} please implement it using Client.create_socket".format(self.clientsock))
        self.clientsock.send(PROTOCOLS.to_bytes(PROTOCOLS.PROTO_ACK))
        recieved = self.clientsock.recv(1)

        if (PROTOCOLS.from_bytes(recieved) == PROTOCOLS.PROTO_ACK):
            self.verified = True
        return self.verified


    def create_socket(self):
        self.clientsock = socket.socket()
    

    
    def connect_to_server(self)->bool:
        try:
            if (not self.clientsock): self.create_socket()
            self.clientsock.connect((self.addr, self.port))
            return self.ack_server()
        except Exception as E:
            return False
    
    def __del__(self):
        if (self.clientsock): self.clientsock.close()
    
    def enocode_data(self, *data:Union[bytes,str])->bytearray:
        bytestream = bytearray()

        for element in data:
            encoded = element.encode() if isinstance(element, str) else element
            datalength = len(encoded)
            lengthBytes = to_bytes(datalength)
            bytestream.extend(lengthBytes)
            bytestream.extend(encoded)
        return bytestream
    
    def send_stream(self, data:Union[bytes,bytearray])->int:
        datalength = len(data)
        start = 0
        while (start < datalength):
            start += self.clientsock.send(data[start:start+self.chunks])
        return start

    def recv_bytes(self, bytedata:bytearray)->bytearray:
        datalength = from_bytes(self.clientsock.recv(2))
        print(datalength)
        start = 0
        tries = 3
        while (start < datalength and tries):
                content = self.clientsock.recv(self.chunks)
                if (not len(content)): tries -= 1
                start += len(content)
                bytedata.extend(content)
    
    def recv_stream(self)->Tuple[PROTOCOLS,bytearray]:
        bytedata = bytearray()
        ack_state = self.clientsock.recv(1)
        print("ack::status::", ack_state)
        accepted = PROTOCOLS.PROTO_REJ
        proto = PROTOCOLS.from_bytes(ack_state)
        if(proto == PROTOCOLS.PROTO_ACK):
            accepted = True
            self.recv_bytes(bytedata)
            accepted = PROTOCOLS.PROTO_ACK
        elif (proto == PROTOCOLS.PROTO_REJ):
            accepted = PROTOCOLS.PROTO_REJ
            self.recv_bytes(bytedata)
        return (accepted, bytedata)
        

    def decode_data(self, data:Union[bytes,bytearray])->List[bytes]:
        lst = []
        datalength = len(data)
        start = 0
        while (start < datalength):
            size = from_bytes(data[start:start+2])
            content = data[start+2:start+2+size]
            start = start+2+size
            lst.append(content)
        return lst
    
    def create_send_packet(self, proto:PROTOCOLS, msg:Union[bytes,bytearray])->bytes:
        return PROTOCOLS.to_bytes(proto)+to_bytes(len(msg))+msg
    
    def query_status(self)->PROTOCOLS:
        return PROTOCOLS.from_bytes(self.clientsock.recv(1))
    

class ClientDB:
    def __init__(self, dbNmae):
        self.dbName = dbNmae
        self.create_tables = False
        self.table_query_script_file = "./userdbschema.sql"
        if not os.path.exists(self.dbName):
            print("Database does not exist, creating one now")
            self.create_tables = True
        self.db = sqlite3.connect(self.dbName, check_same_thread=False)
        self.cursor = self.db.cursor()
        self.init_tables()
        self.cookieManager = CookieManager(self.db)
        self.cookieManager.cookie_table = "CookieStore"
        self.cookieManager.cookieMap[CookieOpt.COOKIE_ID] = 'cookieId'
        self.cookieManager.cookieMap[CookieOpt.COOKIE_USER_ID] = 'userId'
        self.cookieManager.cookieMap[CookieOpt.COOKIE_NAME] = 'cookieName'
        self.cookieManager.cookieMap[CookieOpt.COOKIE_VALUE] = 'cookieValue'
        self.cookieManager.cookieMap[CookieOpt.COOKIE_CREATED] = 'cookieCreate'
        self.cookieManager.cookieMap[CookieOpt.COOKIE_EXPIRED] = 'cookieExpire'

    def get_current_user(self, username:str, userId:int=-1):
        pass

    def inset_user(self, username:str, password:str, userId:int=-1)->bool:
        """
        function to save username and password into local game database
        @params username:str username of user
        @params password:str password of user
        @return boolean True if saved else False
        """
        self.cursor.execute(
            "INSERT INTO Users(userId, userName, userPass, loginUser) values(?, ?, ?, ?)",
            (
                userId if userId > 0 else int.from_bytes(struct.pack("<q", time.time_ns())[:6]),
                username,
                password,
                0
            )
        )
        self.db.commit()
        return True
    
    def init_tables(self):
        if self.create_tables:
            with open(self.table_query_script_file, "r") as query_file:
                self.cursor.executescript(query_file.read())
                query_file.close()
    
    def contains_user(self, userId:int):
        self.cursor.execute(
            "SELECT userName FROM Users WHERE userId=?",(userId,)
        )
        return len(self.cursor.fetchall())
    
    def update_user(self, username:str, password:int, userId:int)->bool:
        QUERY = "UPDATE Users SET userName=?, userPass=? WHERE userId=?"
        self.cursor.execute(QUERY, (username, password, userId))
        self.db.commit()
        return True
    
    def make_default_user(self, userId):
        self.cursor.execute("UPDATE Users SET loginUser=(userid=?)", (userId, ))
        self.db.commit()
    
    def get_default_user(self)->Optional[Tuple[int, str, int, Optional[bytes], int]]:
        self.cursor.execute("SELECT * FROM Users WHERE loginUser=?", (1,))
        user_details = self.cursor.fetchone()
        print(user_details)
        return user_details

    
    def get_cookie(self, username:str, cookieName:str)->Optional[Cookie]:
        self.cursor.execute("SELECT userId from Users WHERE userName=?", (username,))
        userId:int = self.cursor.fetchone()
        print(userId)
        if userId is None: return None
        return self.cookieManager.fetch_cookie(userId[0], cookieName)
        
        
class Player:
    def __init__(self, username, database, cookie):
        self.username = username
        self.database = database
        self.cookie = cookie

class GameUser:
    def __init__(self,clientusername:str, client:Client, client_db:ClientDB):
        self.client = client
        self.clientdb = client_db

        # self.cursor = self.clientdb.cursor()
    
    def register(self, username:str, password:str)->Tuple[PROTOCOLS, Optional[GameMsg], Optional[bytearray]]:
        passencoded = hashlib.sha256(password.encode()).digest()
        content = self.client.enocode_data(username, passencoded)
        data_pack = self.client.create_send_packet(PROTOCOLS.PROTO_REGISTER, content)
        self.client.send_stream(data_pack[:])
        msg, recv_info = None, None
        ack_status:PROTOCOLS = self.client.query_status()
        if (ack_status == PROTOCOLS.PROTO_ACK):
            accepted, recv_info = self.client.recv_stream()
            msg = GameMsg(recv_info[0])
            if (msg == GameMsg.MSG_REGISTER_SUCCESS):
                print("Registration successful.")
                print(recv_info)
                userId:int = decode_msg(recv_info[1:], int)[1]
                print(userId)
                self.clientdb.inset_user(username, password, userId)
                # self.cursor
            else:
                print("GAME SERVER MESSAGE::{}".format(recv_info[1:].decode()))
        return ack_status, msg, recv_info[1:]
            
    
    def login(self, username:str, password:str)->Tuple[PROTOCOLS, Optional[GameMsg], Optional[bytearray]]:
        passencoded = hashlib.sha256(password.encode()).digest()
        content = self.client.enocode_data(username, passencoded)
        data_pack = self.client.create_send_packet(PROTOCOLS.PROTO_LOGIN_CONV, content)
        self.client.send_stream(data_pack)
        ack_status:PROTOCOLS = self.client.query_status()
        if (ack_status == PROTOCOLS.PROTO_ACK):
            accepted, status = self.client.recv_stream()
            msg_status = GameMsg(status[0])
            if (msg_status == GameMsg.MSG_LOGIN_SUCCESS):
                print("Login Successful.", status[1])
                if (status[1] == CookieOpt.COOKIE_START.value):
                    cookie = Cookie.from_bytes(status[1:])
                    print(cookie)
                    if (cookie in self.clientdb.cookieManager):
                        del self.clientdb.cookieManager[cookie]
                    self.clientdb.cookieManager.insertCookie(cookie)
                    if self.clientdb.contains_user(cookie.userId):
                        self.clientdb.update_user(username, password, cookie.userId)
                    else:
                        self.clientdb.inset_user(username, password, cookie.userId)
                    
                    self.clientdb.make_default_user(cookie.userId)
            else:
                print(status[1:].decode())
            
            return ack_status, msg_status, status[1:]
        return ack_status, None, None
    
    def loginCookie(self, username:str):
        print("done")
        cookie = self.clientdb.get_cookie(username, "user_auth")
        if not (cookie.expired()):
            cookieblob = self.client.create_send_packet(PROTOCOLS.PROTO_LOGIN_COOKIE, cookie.to_bytes())
            self.client.send_stream(cookieblob)
            print(self.client.query_status())
            print(self.client.recv_stream())
    
    def createBatch(self, userCookie:Cookie)->Tuple[PROTOCOLS, Optional[GameMsg], Optional[bytearray]]:
        cookieBlob = self.client.create_send_packet(
            PROTOCOLS.PROTO_CREATE_BATCH, 
            userCookie.to_bytes()
        )
        self.client.send_stream(cookieBlob)
        print(self.client.query_status())
        msg = self.client.recv_stream()
        status = msg[0]
        gamemsg:GameMsg = None
        msgstream:bytearray = None
        if (status == PROTOCOLS.PROTO_ACK):
            gamemsg = GameMsg.from_bytes(msg[1].pop(0))
            msgstream = msg[1]
            print(gamemsg)
        return status, gamemsg, msgstream
    
    def getQueueLength(self)->Tuple[PROTOCOLS, Optional[GameMsg], int]:
        self.client.send_stream(
            self.client.create_send_packet(PROTOCOLS.PROTO_GET_QUEUE_LENGTH, b'')
        )
        status, data = self.client.recv_stream()
        gamemsg = None
        length = 4
        if (status == PROTOCOLS.PROTO_ACK):
            gamemsg = GameMsg.from_bytes(data.pop(0))
            if (gamemsg == GameMsg.MSG_QUEUE_LENGTH):
                length = decode_msg(data, int)[1]
        return status, gamemsg, length
    
    def withdrawQueue(self):
        self.client.send_stream(
            self.client.create_send_packet(PROTOCOLS.PROTO_QUEUE_WITHDRAW, b'')
        )
        status, data = self.client.recv_stream()
        print(status, data)
        return True


        
        

    
# clientDB = ClientDB("manu.db")
# client = Client('127.0.0.1', 65432)
# print(client.connect_to_server())
# gameuser = GameUser(None, client, client_db=clientDB)
# if (len(sys.argv) > 1):
#     if (sys.argv[1] == 'login'):
#         gameuser.login("sakshi12","arun1234")
#     elif (sys.argv[1] == 'register'):
#         gameuser.register("sakshi now", "arun123")
#     else:
#         gameuser.loginCookie("sakshi12")
# print(client.clientsock.recv(1))