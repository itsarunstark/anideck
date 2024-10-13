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



from gui.event import Event

FPS = 60
fract:Callable = lambda num: num - math.floor(num) 

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

class GameWindow(window.Window):
    def __init__(self, width, height, *args, **kwargs):
        super().__init__(width, height, "GameWindow", resizable=True, *args, **kwargs)
        self.fps = FPS
        self.gameUser = GameUser(None, gameServer, clientDB)
        clock.schedule_interval(self.update, 1 / self.fps)
        self._network_ip = '127.0.0.1'
        # self.pages:Union[List[Page], Iterable[Page]] = []
        self.batch = graphics.Batch()
        self.order = 0
        self.counter = 0
        self.current_page = None
        self.loading_page = Page(self, 0, 0, 0, 0, color=Color.COLOR_BLUE)
        self._fullscreen = False
        # print(self.gameServer.connect_to_server())
        # self.gameEngine = 


    @property
    def network_ip(self)->str:
        return self._network_ip
    
    @network_ip.setter
    def network_ip(self, value:str):
        self._network_ip = value
    
    def on_resize(self, width, height) -> None:
        super().on_resize(width, height)
        self.current_page.resize(width, height)
        # print(self.width, self.height, width, height)
        # return super().on_resize(width, height)
        ...
    
    def set_page(self, page:Page):
        self.current_page = page
        self.current_page.resize(self.width, self.height)

    def update(self, dt):
        if (self.current_page) : self.current_page.update(dt)
    
    def on_draw(self):
        self.clear()
        # print(button._label.content_height, button._label.content_width)
        # self.current_page.render()
        self.current_page.render()
    
    def on_key_press(self, symbol:int, modifiers:int):
        super().on_key_press(symbol, modifiers)
        if (symbol == key.F11):
            self.set_fullscreen(not self.fullscreen)
        event = Event(EventType.KEYDOWN, 0, 0, symbol, modifiers, 0, 0)
        self.current_page.catch_event(event)
    
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        # super().on_key_release(symbol, modifiers) mvc
        event = Event(EventType.KEYUP, 0, 0, symbol, modifiers)
        self.current_page.catch_event(event)
    
    def add_page(self, page:Page):
        if self.current_page is None:
            self.current_page = page
    
    def on_mouse_enter(self, x: int, y: int) -> None:
        event = Event(
            eventtype=EventType.MOUSEENTER,
            x=x,
            y=y
        )
        self.current_page.catch_event(event)
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        event = Event(
            eventtype=EventType.MOUSEDOWN,
            x=x,
            y=y,
            key=button,
            modifier=modifiers
        )
        self.current_page.catch_event(event)
    
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        event = Event(
            eventtype=EventType.MOUSEUP,
            x=x,
            y=y,
            key=button,
            modifier=modifiers
        )
        self.current_page.catch_event(event)
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        event = Event(
            eventtype=EventType.MOUSEMOTION,
            x=x,
            y=y,
            dx=dx,
            dy=dy
        )
        self.current_page.catch_event(event)


print(Color.COLOR_BLACK)

videoCip = VideoFileClip('assets/loading.mp4')


class WaitPage(Page):
    def __init__(self, win:GameWindow, welcome_img:image.ImageData, *args, **kwargs):

        super().__init__(win, 0, 0, 0, 0, 0, *args, **kwargs)
        self.batch=graphics.Batch()
        self.video_clip: VideoFileClip = videoCip
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
        self.loginJob = Job(gameServer.connect_to_server)
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
    
    def retryAgain(self):
        self.tries = 5
        self.retry = False
        schedular.queueJob(self.loginJob, priority=Priority.PRIORITY_HIGH)


    def onServerConnection(self, job:Job):
        if (job.result == False):
            self.tries -= 1
            print("connection failed")
            if (self.tries): schedular.queueJob(job, priority=Priority.PRIORITY_HIGH)
            else : 
                self.btnRetry.active = True
                self.retry = True
                self.message.opacity = 0
                self.progress_bar.bar.opacity = 0
        
            print("Error in connection")
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
                    schedular.queueJob(self.loginJob, Priority.PRIORITY_HIGH)
                    self.scheduled_login = True
                # self.message.opacity = self.opacity
                # self.progress_bar.bar.opacity = self.opacity
            self.message.opacity = self.imgsprite.opacity
        # print("updating")
        if (self.jumpToPage):
            self.parent.set_page(WelcomePage(self.parent, self.parent.counter))
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

    
class WelcomePage(Page):
    def __init__(self, window:GameWindow, counter, *args, **kwargs):
        # self.batch = graphics.Batch()
        self.parent = window
        super().__init__(window, 0, 0, 0, 0, *args, **kwargs)
        self.batch = graphics.Batch()
        self.color = Color.COLOR_CRIMSON_RED
        self.video_clip = videoCip
        frame = self.video_clip.get_frame(self.parent.counter)
        img = image.ImageData(self.video_clip.w, self.video_clip.h, 'RGB', frame.tobytes(), pitch=-self.video_clip.w*3)
        self.sprite = sprite.Sprite(img, 0, 0, group=graphics.Group(self.order), batch=self.batch)
        self.sprite.scale = self.width/self.video_clip.w
        self.btn1 = Button("Login", self, 1.5*self.width/4, self.height/2, background_color=Color.COLOR_BLACK)
        self.btn1._active_color = Color.COLOR_CRIMSON_RED
        self.btn1._click_color = Color.COLOR_DARK_RED
        self.btn1.onClick(self.btn1Click)
        self.btn2 = Button("Register", self, 2.5*self.width/4, self.height/2, background_color=Color.COLOR_BLACK)
        self.btn2._active_color = Color.COLOR_CRIMSON_RED
        self.btn2._click_color = Color.COLOR_DARK_RED
        self.btn2.onClick(self.btn2Click)
    
    def update(self, dt):
        pass

    def render(self):
        self.parent.counter += 1/self.video_clip.fps
        if (self.parent.counter > self.video_clip.duration) : self.parent.counter = 0
        frame = self.video_clip.get_frame(self.parent.counter)
        self.sprite.image = image.ImageData(self.video_clip.w, self.video_clip.h, 'RGB', frame.tobytes(), pitch=-self.video_clip.w*3)
        self.batch.draw()
    
    def resize(self, width, height):
        super().resize(width, height)
        self.width = width
        self.height = height
        self.sprite.scale = self.width/self.video_clip.w
        new_width = self.width
        new_height = self.sprite.scale*self.video_clip.h
        self.sprite.x = 0
        self.sprite.y = (self.height - new_height)/2
        self.btn1.x = 1.5*self.width/4
        self.btn1.y = self.height/2
        self.btn2.x = 2.5*self.width/4
        self.btn2.y = self.height/2
        self.btn1.widget_resolve()
        self.btn2.widget_resolve()

    
    def btn1Click(self):
        "Clear func is called"
        self.parent.set_page(LoginPage(self.parent))
    
    def btn2Click(self):
        self.parent.set_page(RegisterPage(self.parent))



        # print("yes")


class RegisterPage(Page):
    def __init__(self, parent:GameWindow):
        super().__init__(parent, 0, 0, 0, 0)
        self.parent:GameWindow = self.parent
        self.color = (0, 0, 0, 0)
        self.batch = graphics.Batch()
        self.video_clip = videoCip

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
        schedular.queueJob(
            self.registerJob
        )

    
    def update(self, dt):
        super().update(dt)
        if (self.statusTextChanged):
            self.status.text = self.statustext
            self.statusTextChanged = False
        
        if (self.promptToRegisterPage):
            self.parent.set_page(LoggingPage(self.parent))
    
    # def render(self):
    #     self.batch.draw()

    def goBack(self):
        self.parent.set_page(WelcomePage(self.parent, self.parent.counter))
    
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

class ConnectionPage(Page):
    def __init__(self, parent:GameWindow):
        super().__init__(parent, 0, 0, 0, 0)
        self.batch = graphics.Batch()
        self.parent:GameWindow = parent
        self.welcomeText = text.Label(text="ANIDECK", font_size=45, batch=self.batch, group=graphics.Group(self.order+1))
        self.welcomeText.anchor_x = 'center'
        self.welcomeText.anchor_y = 'center'
        self.welcomeText.x = self.width/2
        self.welcomeText.y = self.height/2
        self.animation_time = 2.0
        self.counter = 0
        self.color = Color.COLOR_CRIMSON_RED
        self.opacity = 0
        
    def update(self, dt):...
        # self.batch.draw()
    
    def resize(self, width, height):
        super().resize(width, height)
        self.welcomeText.x = width/2
        self.welcomeText.y = height/2
    
    def render(self):
        self.counter += 1/self.parent.fps
        x0 = (math.sin((self.counter*math.pi)/self.animation_time - math.pi/2) + 1)/2
        self.welcomeText.opacity = int(x0*255)
        if (self.counter > self.animation_time*2):
            self.parent.set_page(WaitPage(self.parent, None))
        self.batch.draw()
    
    def __del__(self):
        print("PAGE DELETED FROM MEMORY")
        # self.color 

class LoginPage(Page):
    def __init__(self, parent:GameWindow):
        super().__init__(parent, 0, 0, 0, 0)
        self.batch = graphics.Batch()
        self.parent: GameWindow = parent
        self.username = InputBox(self, self.width/2, 2.5*self.height/4, "username", 26)
        self.password = InputBox(self, self.width/2, 1.5*self.height/4, "password", 26)
        self.password.maskfunction = lambda x:'#'
        self.color = Color.COLOR_CRIMSON_RED
        self.video_clip = videoCip
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
        self.lock = Lock()
        self.showText = 0
        # self.goBack.widget_resolve()
    
    def update(self, dt):
        super().update(dt)
        if (self.switchToLogin):
            self.parent.set_page(LoggingPage(self.parent))
    
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
        self.parent.set_page(WelcomePage(self.parent, self.parent.counter))
    
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
        schedular.queueJob(job, Priority.PRIORITY_HIGH)
    
    def onLoginFinished(self, job:Job):
        valid, status, result = job.result
        if (valid == PROTOCOLS.PROTO_ACK):
            if (status == GameMsg.MSG_LOGIN_SUCCESS):
                self.statusmsg = "server :: login succesful"
                self.switchToLogin = True
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


class LoggingPage(Page):
    def __init__(self, parent:GameWindow):
        super().__init__(parent, 0, 0, 0, 0)
        self.parent:GameWindow = parent
        self.video_clip = videoCip
        frame = self.video_clip.get_frame(parent.counter)
        img = image.ImageData(self.video_clip.w, self.video_clip.h, "RGB", frame.tobytes(), -self.video_clip.w*3)
        self.sprite = sprite.Sprite(img, 0, 0, group=graphics.Group(self.order+1), batch=self.batch)
        self.sprite.scale = self.width/self.video_clip.w
        self.loggingMsg = text.Label(text="Logging In.... Please Wait", anchor_x='center', anchor_y='center', batch=self.batch, group=self.sprite.group)
        # self.progress_bar = Progressbar(self, 50, 50, self.width/2, 10, self.batch, anchor=Anchor.ANCHOR_LEFT)
        # self.progress_bar.progress = 100
        # self.progress_bar.widget_resolve()
    def resize(self, width, height):
        super().resize(width=width, height=height)
        self.loggingMsg.x = self.width/2
        self.loggingMsg.y = self.height/2
        self.sprite.scale = self.width/self.video_clip.w
        self.sprite.x = 0
        self.sprite.y = (self.height - self.sprite.scale*self.video_clip.h)/2


    def render(self):
        self.parent.counter += 1/self.video_clip.fps
        if (self.parent.counter > self.video_clip.duration): self.parent.counter = 0
        frame = self.video_clip.get_frame(self.parent.counter)
        img = image.ImageData(self.video_clip.w, self.video_clip.h, "RGB", frame.tobytes(), -self.video_clip.w*3)
        self.sprite.image = img
        self.batch.draw()


# img = image.load(os.path.join("assets", "loading.bmp"))
width = 1000
ratio = videoCip.h/videoCip.w
window = GameWindow(width, int(ratio*width), vsync=False, fullscreen=False)
ConnectionPage(window).add()
# LoggingPage(window).add()
# window.set_fullscreen(True)

# button = Button("Hello", page,page.width/2 ,page.height/2, _anchor=Anchor.ANCHOR_CENTER)
# label = Text("Connecting to server", page, 0, 0, _anchor=Anchor.ANCHOR_LEFT)
# button2 = Button("Hello", page,, _anchor=Anchor.ANCHOR_CENTER)
app.run()