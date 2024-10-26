from pyglet import window, shapes, graphics, clock, image, sprite, app, gl, text
from pyglet.window import key
from gui.page import Page
from gui.color import Color
from gamewindow import GameWindow
from gui.event import Event, EventType
from schedular import Job, Priority
from gui.progressbar import Progressbar
from gui.button import Button
from gui.inputbox import InputBox
from gui.anchor import Anchor
from network import PROTOCOLS, GameMsg
from network.cookiejar import Cookie
import loggingpage
import guildpage
import re

import math
from tools import *
import welcomepage

class LoginPage(Page):
    def __init__(self, parent:GameWindow):
        super().__init__(parent, 0, 0, 0, 0)
        self.batch = graphics.Batch()
        self.parent: GameWindow = parent
        self.username = InputBox(self, self.width/2, 2.5*self.height/4, "username", 26)
        self.password = InputBox(self, self.width/2, 1.5*self.height/4, "password", 26)
        self.password.maskfunction = lambda x:'#'
        self.color = Color.COLOR_CRIMSON_RED
        self.video_clip = self.parent.videoClip
        frame = self.video_clip.get_frame(parent.counter)
        img = image.ImageData(self.video_clip.w, self.video_clip.h, "RGB", frame.tobytes(), -self.video_clip.w*3)
        self.sprite = sprite.Sprite(img, 0, 0, group=graphics.Group(self.order+1), batch=self.batch)
        self.sprite.scale = self.width/self.video_clip.w
        self.loginBtn = Button("Login", self, self.width/2, self.height/4, font_color=Color.COLOR_WHITE, background_color=Color.COLOR_GREY)
        self.loginBtn._active_color = Color.COLOR_CRIMSON_RED
        self.loginBtn._click_color = Color.COLOR_DARK_RED
        self.loginBtn.active = False
        self.username.oninput = self.on_input
        self.password.oninput = self.on_input
        self.userregx = "^[a-zA-Z][a-zA-Z0-9_-]{2,19}$"
        self.passregx = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$"
        self.username.active_color = Color.COLOR_CRIMSON_RED
        self.password.active_color = Color.COLOR_CRIMSON_RED
        self.loginBtn.onClick(self.on_click)
        self.backBtn = Button("Go Back", self, 0, 0, _anchor=Anchor.ANCHOR_LEFT|Anchor.ANCHOR_TOP, font_size=12, background_color=(0,0,0,0))
        self.backBtn._active_color = (0,0,0,0)
        self.backBtn._click_color = (0,0,0,0)
        self.backBtn.onClick(self.goBack)
        self.backBtn.x = self.backBtn.boundbox.w/2
        self.backBtn.y = self.backBtn.boundbox.h/2
        self.switchToLogin = False
        self.status_text = text.Label(
            "status message goes here", 
            0, 
            self.height,
            # font_name='Consolas', 
            anchor_x='left', 
            anchor_y='top', 
            batch=self.batch, 
            group=graphics.Group(self.order+1)
        )
        self.status_text.visible = False
        self.statusmsgChanged = 0
        self.statusmsg = self.status_text.text
        self.showText = 0
        # self.goBack.widget_resolve()
    
    def update(self, dt):
        super().update(dt)
        if (self.switchToLogin):
            self.parent.set_page(guildpage.GuildPage(self.parent))
    
    def render(self):
        if (self.showText != self.status_text.visible): self.status_text.visible = self.showText
        if (self.statusmsgChanged):
            self.statusmsgChanged = 0
            self.status_text.text = self.statusmsg
        self.parent.counter += 1/self.video_clip.fps
        if (self.parent.counter > self.video_clip.duration): self.parent.counter = 0
        frame = self.video_clip.get_frame(self.parent.counter)
        img = image.ImageData(self.video_clip.w, self.video_clip.h, "RGB", frame.tobytes(), -self.video_clip.w*3)
        self.sprite.image = img
        self.batch.draw()
    
    def resize(self, width, height):
        self.width = width
        self.height = height
        self.sprite.scale = self.width/self.video_clip.w
        self.sprite.x = 0
        self.sprite.y = (self.height - self.sprite.scale*self.video_clip.h)/2
        self.username.x = self.width/2
        self.username.y = 2.1*self.height/4
        self.password.x = self.width/2
        self.password.y = 1.8*self.height/4
        self.loginBtn.x = self.width/2
        self.loginBtn.y = self.height/4
        self.loginBtn.widget_resolve()
        self.backBtn.x = self.backBtn.boundbox.w/2
        self.backBtn.y = self.backBtn.boundbox.h/2
        self.backBtn.widget_resolve()
        self.status_text.y = self.height
    
    def goBack(self):
        self.parent.set_page(welcomepage.WelcomePage(self.parent, self.parent.counter))
    
    def on_input(self):
        username = ''.join(self.username.inputseq)
        password = ''.join(self.password.inputseq)
        match1 = bool(re.match(self.userregx, username))
        match2 =  len(password) > 4
        self.username.active_color = Color.COLOR_GREEN if match1 else Color.COLOR_CRIMSON_RED
        self.password.active_color = Color.COLOR_GREEN if match2 else Color.COLOR_CRIMSON_RED
        print(f"called {username} {password}")
        if (match1 and match2):
            self.loginBtn.active = True
            self.loginBtn.background_color = Color.COLOR_BLACK
        else:
            self.loginBtn.active = False
            self.loginBtn.background_color = Color.COLOR_GREY
        self.loginBtn._background_rect.color = self.loginBtn.background_color
    
    def on_click(self):
        self.loginBtn.active = False
        self.username.readonly = True
        self.password.readonly = True
        job = Job(self.execute_login)
        job.callback_function = self.onLoginFinished
        self.parent.schedular.queueJob(job, Priority.PRIORITY_HIGH)
    
    def onLoginFinished(self, job:Job):
        valid, status, result = job.result
        if (valid == PROTOCOLS.PROTO_ACK):
            if (status == GameMsg.MSG_LOGIN_SUCCESS):
                self.statusmsg = "server :: login successful"
                self.switchToLogin = True
                print("GME:STATUS::{}".format(result))
                self.parent.current_user = {
                    "cookie": Cookie.from_bytes(result),
                    "username": ''.join(self.username.inputseq)
                }
                print("CURRENT_USER::: {}".format(self.parent.current_user))

            else:
                self.statusmsg = ("server :: {} :: {}".format(status.name, result.decode()))
                self.loginBtn.active = True
                self.username.readonly = False
                self.password.readonly = False
        else:
            self.statusmsg = "server :: {}".format(valid.name)
            self.loginBtn.active = True
            self.username.readonly = False
            self.password.readonly = False
        self.statusmsgChanged = 1
        self.showText = 1

    def execute_login(self):
        return self.parent.gameUser.login(''.join(self.username.inputseq), ''.join(self.password.inputseq))
        # self.parent.set_page(waitingPage)
