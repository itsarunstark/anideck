import os
import glob
import re
import math
import socket
from gui import *
from pyglet import window, shapes, graphics, clock, image, sprite, app, gl
from enum import Enum
from moviepy.editor import VideoFileClip
from pyglet.window import Window, key
from typing import List,Union,Iterable, Callable, Dict, Any
from client import Client, ClientDB, GameUser
from schedular import Schedular, SchedularState, Job, Priority
from network import GameMsg, PROTOCOLS
from threading import Lock
from gamewindow import GameWindow
from connectionpage import ConnectionPage
from waitpage import WaitPage


from gui.event import Event

FPS = 60


def get_ip_address():
    s = socket.socket()
    s.connect(('1.1.1.1', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


# ip_address = get_ip_address()

schedular = Schedular()
schedular.start()
print("INFO::STARTED SCHEDULAR")
clientDB = ClientDB("manu.db")
gameServer = Client("127.0.0.1", port=65432)




print(Color.COLOR_BLACK)

videoCip = VideoFileClip('assets/loading.mp4')

        # print("yes")
        # self.color 



# img = image.load(os.path.join("assets", "loading.bmp"))
width = 1000
ratio = videoCip.h/videoCip.w
window = GameWindow(width, int(ratio*width), gameServer, clientDB, vsync=False, fullscreen=False)
window.videoClip = videoCip
window.gameServer = gameServer
window.schedular = schedular
window.clientDB = clientDB
ConnectionPage(window).add()
# LoggingPage(window).add()
# window.set_fullscreen(True)

# button = Button("Hello", page,page.width/2 ,page.height/2, _anchor=Anchor.ANCHOR_CENTER)
# label = Text("Connecting to server", page, 0, 0, _anchor=Anchor.ANCHOR_LEFT)
# button2 = Button("Hello", page,, _anchor=Anchor.ANCHOR_CENTER)
app.run()