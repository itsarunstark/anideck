import select
import os
import sys
import socket
from typing import Union,List
import sqlite3
import struct

class NetworkTool:

    @staticmethod
    def get_addr_info():
        s = socket.socket()
        s.connect(('1.1.1.1', 80))
        addr = s.getsockname()[0]
        s.close()
        return addr
    
    @staticmethod
    def ping_networks(networkbase:str)->List[str]:
        netmask = list(map(int, networkbase.split(".")))
        netmask[-1] = 0
        networks = []
        for i in range(0, 255):
            s = socket.socket()
            s.settimeout(0.200)
            netmask[-1] = i
            print(netmask)
            try:
                s.connect(('%d.%d.%d.%d'%tuple(netmask), 65432))
                networks.append('%d.%d.%d.%d'%tuple(netmask))
                s.close()
            except socket.timeout:
                print("timeout")
        return networks

class MessageFormat:
    identifyFormat = "sIXs" #id #username #padding, #cookie  

class CookieJar:
    def __init__(self, filename):
        self.filename = filename
        self.create = True
        if not os.path.exists(self.filename):
            self.create = True
        self.database = sqlite3.connect(filename)
        self.dbschema = "./userdbschema.sql"
        self.cookies = bytearray()
        self.cursor = self.database.cursor()
        
    
    def fetch_cookies(self):
        if (self.create):
            self.cursor.executescript(open(self.dbschema, "r").read())
            print("Executed script")
        cookies = {}

        self.database.commit()
        

            
            
        

class NetworkBuddy:
    def __init__(self, addr_info:Union[str,bytes], port:int):
        self.addr_info = addr_info
        self.port = port
        self.socket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cookiejar 
    
    def connect(self)->bool:
        self.socket.connect((self.addr_info, self.port))

if __name__ == '__main__':
    # serverAddress = NetworkTool.ping_networks(NetworkTool.get_addr_info())[0]
    # buddy = NetworkBuddy(serverAddress, 65432)
    jar = CookieJar("manu.db")
    jar.fetch_cookies()
