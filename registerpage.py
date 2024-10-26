from pyglet import window, shapes, graphics, clock, image, sprite, app, gl, text
from gui.page import Page
from gui.color import Color
from gamewindow import GameWindow
from gui.event import Event, EventType
from schedular import Job, Priority
from gui.progressbar import Progressbar
from gui.button import Button
from gui.inputbox import InputBox
from gui.anchor import Anchor
import math
import welcomepage
import re
import loggingpage
from network import PROTOCOLS, GameMsg
from tools import *


class RegisterPage(Page):
    def __init__(self, parent:GameWindow):
        super().__init__(parent, 0, 0, 0, 0)
        self.parent:GameWindow = self.parent
        self.color = (0, 0, 0, 0)
        self.batch = graphics.Batch()
        self.video_clip = self.parent.videoClip

        frame = self.video_clip.get_frame(parent.counter)
        self.img = image.ImageData(self.video_clip.w, self.video_clip.h, "RGB", frame, pitch=-3*self.video_clip.w)
        self.imgsprite = sprite.Sprite(self.img, 0, 0, group=graphics.Group(self.order-1), batch=self.batch)
        self.imgsprite.scale = self.width/self.img.width
        self.userfield = InputBox(self, self.width/2, 5*self.height/9, "username")
        self.passfield = InputBox(self, self.width/2, 3*self.height/9, "password")
        self.cpassfield = InputBox(self, self.width/2, self.height/9, "confirm password")
        self.userfield.oninput = self.passfield.oninput = self.cpassfield.oninput = self.on_input
        self.registerBtn = Button("Register", self, self.width/2, self.height/2, background_color=Color.COLOR_GREY)
        self.registerBtn._active_color = Color.COLOR_CRIMSON_RED
        self.registerBtn._click_color = Color.COLOR_DARK_RED
        self.registerBtn.background_color = Color.COLOR_GREY
        self.registerBtn.active = False
        self.status = text.Label("", 0, self.height, anchor_y="top", batch=self.batch, group=graphics.Group(self.order+1))
        self.backBtn = Button("Go back", self, 0, 0, font_size=12, background_color=(0,0,0,0), _anchor=Anchor.ANCHOR_LEFT|Anchor.ANCHOR_TOP)
        self.backBtn._active_color = (0,0,0,0)
        self.backBtn._click_color = (0,0,0,0)
        self.backBtn.onClick(self.goBack)
        self.backBtn.x = self.backBtn.boundbox.w/2
        self.backBtn.y = self.backBtn.boundbox.h/2
        self.registerJob = Job(self.onRegisterJob)
        self.registerJob.callback_function = self.onRegistrationFinised
        self.statustext = ""
        self.statusTextChanged = False
        self.promptToRegisterPage = False
    
    def on_click(self):
        self.registerBtn.active = False
        self.parent.schedular.queueJob(
            self.registerJob
        )

    
    def update(self, dt):
        super().update(dt)
        if (self.statusTextChanged):
            self.status.text = self.statustext
            self.statusTextChanged = False
        
        if (self.promptToRegisterPage):
            self.parent.set_page(loggingpage.LoggingPage(self.parent))
    
    # def render(self):
    #     self.batch.draw()

    def goBack(self):
        self.parent.set_page(welcomepage.WelcomePage(self.parent, self.parent.counter))
    
    def catch_event(self , event:Event):
        super().catch_event(event)
        # print(event, self.active_widget)
    
    def resize(self, width, height):
        super().resize(width, height)
        self.userfield.x = self.width/2
        self.userfield.y = 2.7*self.height/4
        self.passfield.x = self.width/2
        self.passfield.y = self.userfield.y - self.userfield.boundbox.h - 10
        self.cpassfield.y = self.passfield.y - self.passfield.boundbox.h - 10
        self.cpassfield.x = self.width/2
        self.registerBtn.y = self.cpassfield.boundbox.y - self.cpassfield.boundbox.h - 10
        self.registerBtn.x = self.width/2
        self.registerBtn.onClick(self.on_click)
        self.imgsprite.scale = self.width/self.img.width
        self.imgsprite.y = self.height/2 - self.img.height*self.imgsprite.scale/2
        self.registerBtn.widget_resolve()
        self.backBtn.x = self.backBtn.boundbox.w/2
        self.backBtn.y = self.backBtn.boundbox.h/2
        self.backBtn.widget_resolve()
        self.registerBtn.y = self.height
        
    
    def render(self):
        self.parent.counter += 1/self.parent.fps
        if (self.parent.counter > self.video_clip.duration):
            self.parent.counter = 0
        frame = self.video_clip.get_frame(self.parent.counter)
        self.img = image.ImageData(self.video_clip.w, self.video_clip.h, "RGB", frame, pitch=-3*self.video_clip.w)
        self.imgsprite.image = self.img
        self.batch.draw()
        self.userregx = "^[a-zA-Z][a-zA-Z0-9_-]{2,19}$"
    
    def onRegisterJob(self):
        username = ''.join(self.userfield.inputseq)
        password = ''.join(self.passfield.inputseq)
        return self.parent.gameUser.register(username, password)
    
    def onRegistrationFinised(self, job:Job):
        result = self.registerJob.result
        status:PROTOCOLS = result[0]
        msg:GameMsg = result[1]
        info:bytearray = result[2]
        if (status == PROTOCOLS.PROTO_ACK):
            if (msg == GameMsg.MSG_REGISTER_SUCCESS):
                self.promptToRegisterPage = True
                return
            self.statustext = "SERVER::{}::{}".format(msg.name, info.decode())
        else:
            self.statustext = "SERVER::{}".format(status.name)
        self.statusTextChanged = True
        self.registerBtn.active = True

    def on_input(self):
        username = ''.join(self.userfield.inputseq)
        password = ''.join(self.passfield.inputseq)
        cpassword = ''.join(self.cpassfield.inputseq)
        match1 = bool(re.match(self.userregx, username))
        match2 = len(password) > 4
        match3 = (cpassword == password)
        # print("Receiving input")
        self.userfield.active_color = Color.COLOR_GREEN if match1 else Color.COLOR_RED
        self.passfield.active_color = Color.COLOR_GREEN if match2 else Color.COLOR_RED
        self.cpassfield.active_color = Color.COLOR_GREEN if match3 else Color.COLOR_RED
        if (match1 and match2 and match3):
            self.registerBtn.active = True
            # self.userfield.text_label.color = Color.COLOR_GREEN
            self.registerBtn._background_color = Color.COLOR_BLACK
        else:
            self.registerBtn.active = False
            self.registerBtn._background_color = Color.COLOR_GREY
        self.registerBtn._background_rect.color = self.registerBtn.background_color