import socket
import select
import sys
import time
import logging
from typing import List

def get_ip_address():
    s = socket.socket()
    s.connect(('1.1.1.1', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

class ColorFormatter(logging.Formatter):
    red = '\x1b[31;1m'
    green = '\x1b[32;0m'
    yellow = '\x1b[33;0m'
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



class Server:
    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.batchsize = 10
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
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
        
        while self.isRunning:
            readables, writables, exceptables = select.select(
                inputs,[],[], 0
            )
            for readable in readables:
                if (readable is self.socket):
                    dev, addr = readable.accept()
                    inputs.add(dev)
                    print(dev)
                    dev.sendall('Length:34 GAY'.encode())
                else:
                    print("Some clients want to send message")
                    print(readable.recv(1024))
            if len(writables):
                print(writables)

    def __del__(self):
        self.socket.close()
        logger.log(logging.INFO, "Shutting down server")


ip_address = get_ip_address()
logger.log(logging.DEBUG, "Server IP: {}".format(ip_address))
server = Server(ip_address, 65432)
server.Serve()
del server