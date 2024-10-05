import socket
from typing import Tuple, List, Set, Union, Callable
from network import PROTOCOLS
import hashlib

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
        if (not self.clientsock): self.create_socket()
        self.clientsock.connect((self.addr, self.port))
        return self.ack_server()
    
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
    
    def recv_stream(self)->Union[bytes,bytearray]:
        bytedata = bytearray()
        ack_state = self.clientsock.recv(1)
        proto = PROTOCOLS.from_bytes(ack_state)
        if(proto & PROTOCOLS.PROTO_ACK):
            datalength = from_bytes(self.clientsock.recv(2))
            print(datalength)
            start = 0
            tries = 3
            while (start < datalength and tries):
                content = self.clientsock.recv(self.chunks)
                if (not len(content)): tries -= 1
                start += len(content)
                bytedata.extend(content)
        return bytedata

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
    
    def create_send_packet(self, proto:PROTOCOLS, msg:Union[bytes,bytearray]):
        return PROTOCOLS.to_bytes(proto)+to_bytes(len(msg))+msg
    
    def query_status(self)->PROTOCOLS:
        return PROTOCOLS.from_bytes(self.clientsock.recv(1))
    

    

class GameUser:
    def __init__(self,client:Client):
        self.client = client
    
    def register(self, username:str, password:str)->bool:
        passencoded = hashlib.sha256(password.encode()).digest()
        content = self.client.enocode_data(username, passencoded)
        data_pack = self.client.create_send_packet(PROTOCOLS.PROTO_REGISTER, content)
        self.client.send_stream(data_pack[:])
        ack_status:PROTOCOLS = self.client.query_status()
        if (ack_status & PROTOCOLS.PROTO_ACK):
            recv_info = self.client.recv_stream()
            print(recv_info)
        

    

client = Client('127.0.0.1', 65432)
print(client.connect_to_server())
gameuser = GameUser(client)
gameuser.register("hello","sakshi")
# print(client.clientsock.recv(1))