import socket
import select
import sys
import time
import logging
from typing import List
from .network import PROTOCOLS
def get_ip_address():
    s = socket.socket()
    s.connect(('1.1.1.1', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip





class Server:
    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.batchsize = 10
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.setblocking(False)
        self.isRunning = True
        try:
            self.socket.bind((host, port))
            logger.info( "Listening on {}:{}".format(host, port))
        except socket.error as e:
            logger.log(logging.FATAL , "Failed to bind to {}:{}".format(host, port))
            sys.exit(1)
    

    def Serve(self):
        self.socket.listen(self.batchsize)
        inputs = {self.socket}
        readables : List[socket.socket]
        writables : List[socket.socket]
        exceptables: List[socket.socket]
        removeindex = set()
        while self.isRunning:
            readables, writables, exceptables = select.select(
                inputs,[],[], 0
            )
            # print(readables)
            removeindex.clear()
            for index, readable in enumerate(readables):
                if (readable is self.socket):
                    dev, addr = readable.accept()
                    inputs.add(dev)
                    dev.sendall('Length:34'.encode())
                else:
                    print("Some clients want to send message")
                    try:
                        print(readable.recv(1024))
                    except ConnectionResetError as E:
                        print(str(E))
                        inputs.remove(readable)
                        removeindex.add(index)
                    except ConnectionAbortedError as E:
                        inputs.remove(readable)
                        print(str(E))
                        removeindex.add(index)


            oldoffset = 0

            for removable in removeindex:
                readables.pop(removable+oldoffset)
                oldoffset -= 1


    def __del__(self):
        self.socket.close()
        logger.log(logging.INFO, "Shutting down server")


ip_address = get_ip_address()
logger.log(logging.DEBUG, "Server IP: {}".format(ip_address))
server = Server(ip_address, 65432)
server.Serve()
del server