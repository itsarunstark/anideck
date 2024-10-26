from pyglet import window, shapes, graphics, clock, image, sprite, app, gl, text
from gui.page import Page
from gui.color import Color
from gamewindow import GameWindow
from gui.event import Event, EventType
from schedular import Job, Priority
from gui.progressbar import Progressbar
from gui.button import Button
from welcomepage import WelcomePage
from network import PROTOCOLS, GameMsg
from network.cookiejar import Cookie
import math
from tools import *
import guildpage

class WaitPage(Page):
    def __init__(self, win:GameWindow, welcome_img:image.ImageData, *args, **kwargs):

        super().__init__(win, 0, 0, 0, 0, 0, *args, **kwargs)
        self.parent:GameWindow = win
        self.batch=graphics.Batch()
        self.video_clip: VideoFileClip = win.videoClip
        self.parent.counter = 0
        self.parent.height = (self.width*self.video_clip.h)//self.video_clip.w
        self.group = graphics.Group(self.order-1)
        frame = self.video_clip.get_frame(self.parent.counter)
        self.img = image.ImageData(self.video_clip.w, self.video_clip.h, 'RGB', frame.tobytes())
        self.imgsprite = sprite.Sprite(self.img, x=0, y=0, batch=self.batch, group=self.group)
        self.imgsprite.scale_x = self.height / self.img.height
        self.imgsprite.scale_y = self.height / self.img.height
        self.color = (0, 0, 0, 50)
        self.runtime = 0.0
        self.tries = 5
        self.opacity = 0
        self.imgsprite.opacity = 0
        self.message = text.Label(
            text="Connecting to server",
            # font_name="Consolas",
            font_size=24,
            x=self.width//2,
            y=self.height//2,
            color=Color.COLOR_WHITE,
            batch=self.batch,
            group=graphics.Group(self.order+1),
            anchor_x='center',
            anchor_y='center'
        )
        self.message.opacity = 0
        self.loginJob = Job(self.parent.gameServer.connect_to_server)
        self.loginJob.callback_function = self.onServerConnection
        self.progress_bar = Progressbar(self, self.width/2, self.height/5, 100, 10)
        self.progress_bar.bar.opacity = 0
        self.animation_time = 5.0
        self.scheduled_login = False
        self.btnRetry = Button("Retry", self, self.width/2, self.height/2, background_color=Color.COLOR_BLACK)
        self.btnRetry._active_color = Color.COLOR_CRIMSON_RED
        self.btnRetry._click_color = Color.COLOR_DARK_RED
        self.btnRetry.active = False
        self.btnRetry.batch = None
        self.btnRetry._label.batch = None
        self.btnRetry._background_rect.batch = None
        self.retry = False
        self.connected = False
        self.btnRetry.onClick(self.retryAgain)
        self.jumpToPage = 0
        self.defaultuser = self.parent.clientDB.get_default_user()
        self.defaultLoginJob:Job = None
        if self.defaultuser:
            self.defaultLoginJob = Job(self.try_login, self.defaultuser[1], self.defaultuser[2])
            self.defaultLoginJob.callback_function = self.validate_login
    
    def validate_login(self, job:Job):
        PROTO, CODE, MSG = job.result[0]
        username = job.result[1]
        if (PROTO == PROTOCOLS.PROTO_ACK and CODE == GameMsg.MSG_LOGIN_SUCCESS):
            self.parent.current_user = {
                "cookie": Cookie.from_bytes(MSG),
                "username": username
            }
            self.jumpToPage = 0xff
        else:
            self.jumpToPage = 1
        


    def try_login(self, username:str, password:str):
        return self.parent.gameUser.login(username, password), username

    def retryAgain(self):
        self.tries = 5
        self.retry = False
        self.parent.schedular.queueJob(self.loginJob, priority=Priority.PRIORITY_HIGH)


    def onServerConnection(self, job:Job):
        if (job.result == False):
            self.tries -= 1
            print("connection failed")
            if (self.tries): 
                self.parent.schedular.queueJob(job, priority=Priority.PRIORITY_HIGH)
            else : 
                self.btnRetry.active = True
                self.retry = True
                self.message.opacity = 0
                self.progress_bar.bar.opacity = 0
        
            print("Error in connection")
        else:
            if (self.defaultuser):
                self.parent.schedular.queueJob(self.defaultLoginJob, priority=Priority.PRIORITY_MID)
                self.tries = 5
            else:
                self.jumpToPage = 1

    def update(self, dt):

        self.runtime += dt
        if not self.retry:
            self.progress_bar.x = self.width/2 + math.sin((fract(self.runtime)-0.5)*math.pi)*300
            self.progress_bar.bar.opacity = int(255*math.cos((fract(self.runtime)-0.5)*math.pi)*(math.floor(self.runtime)%2))
            self.progress_bar.widget_resolve()
            if (self.runtime < self.animation_time):
                self.imgsprite.opacity = int(255*(
                    (math.sin(-math.pi/2 + (self.runtime/self.animation_time)*math.pi)+1)/2
                ))
            else:
                if (not self.scheduled_login):
                    self.parent.schedular.queueJob(self.loginJob, Priority.PRIORITY_HIGH)
                    self.scheduled_login = True
                # self.message.opacity = self.opacity
                # self.progress_bar.bar.opacity = self.opacity
            self.message.opacity = self.imgsprite.opacity
        # print("updating")
        if (self.jumpToPage == 1):
            self.parent.set_page(WelcomePage(self.parent, self.parent.counter))
        if (self.jumpToPage == 0xff):
            self.parent.set_page(guildpage.GuildPage(self.parent))
        return super().update(dt)


    def loadfunction(self,x):
        return math.sin(x)


    def resize(self, width, height):
        self.width = width
        self.height = height
        self.imgsprite.scale_x = width/self.img.width
        self.imgsprite.scale_y = width/self.img.width
        new_width = width
        new_height = self.img.height * (width/self.img.width)
        self.imgsprite.x = (self.width - new_width)//2
        self.imgsprite.y = (self.height - new_height)//2
        self.message.x = width//2
        self.message.y = height//2
        self.progress_bar.x = width/2
        self.progress_bar.y = height/5
        self.progress_bar.widget_resolve()
        self.btnRetry.x = self.width/2
        self.btnRetry.y = self.height/2
        self.btnRetry.widget_resolve()
        # self.loginJob
    def render(self):
        self.parent.counter += 1/self.video_clip.fps
        if (self.parent.counter > self.video_clip.duration):self.parent.counter = 0
        frame = self.video_clip.get_frame(self.parent.counter)
        self.img = image.ImageData(self.video_clip.w, self.video_clip.h, 'RGB', frame.tobytes(), pitch=-self.video_clip.w*3)
        self.imgsprite.image = self.img
        self.batch.draw()
        if self.retry:
            self.btnRetry._background_rect.draw()
            self.btnRetry._label.draw()
        # print(self.imgsprite.opacity)
        # print("rendering")
