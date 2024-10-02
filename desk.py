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
        

class GameWindow(window.Window):
    def __init__(self, width, height, *args, **kwargs):
        super().__init__(width, height, "GameWindow", resizable=True, *args, **kwargs)
        self.fps = FPS
        clock.schedule_interval(self.update, 1 / self.fps)
        self._network_ip = '127.0.0.1'
        self.pages:Union[List[Page], Iterable[Page]] = []
        self.batch = graphics.Batch()
        self.order = 0
        self.counter = 0
        self.current_page = None
        self.loading_page = Page(self, 0, 0, 0, 0, color=Color.COLOR_BLUE)
        self._fullscreen = False


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
        # super().on_key_release(symbol, modifiers)
        event = Event(EventType.KEYUP, 0, 0, symbol, modifiers)
        self.current_page.catch_event(event)
    
    def add_page(self, page:Page):
        self.pages.append(page)
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
    def __init__(self, win, welcome_img:image.ImageData, *args, **kwargs):

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
        # self.input = InputBox(self, self.width/2, self.height/2, "Hello", 34)
        # self.loader = shapes.Arc(x=400, y=300, radius=100, angle=1, color=(255, 0, 0), batch=self.batch, group=graphics.Group(self.order+10), thickness=3)
        self.message = text.Label(
            text="Connecting to server",
            font_name="Consolas",
            font_size=24,
            x=self.width//2,
            y=self.height//2,
            color=Color.COLOR_WHITE,
            batch=self.batch,
            group=graphics.Group(self.order+1),
            anchor_x='center',
            anchor_y='center'
        )

        self.progress_bar = Progressbar(self, self.width/2, self.height/5, 100, 10)
        self.progress_bar.bar.opacity = 123
        

    def update(self, dt):
        self.runtime += dt
        self.progress_bar.x = self.width/2 + math.sin((fract(self.runtime)-0.5)*math.pi)*300
        self.progress_bar.bar.opacity = int(255*math.cos((fract(self.runtime)-0.5)*math.pi)*(math.floor(self.runtime)%2))
        self.progress_bar.widget_resolve()
        # print("updating")
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
    
    def render(self):
        self.parent.counter += 1/self.video_clip.fps
        if (self.parent.counter > self.video_clip.duration):self.parent.counter = 0
        frame = self.video_clip.get_frame(self.parent.counter)
        self.img = image.ImageData(self.video_clip.w, self.video_clip.h, 'RGB', frame.tobytes(), pitch=-self.video_clip.w*3)
        self.imgsprite.image = self.img
        self.batch.draw()
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
        self.parent.set_page(loginPage)

        # print("yes")

class LoginPage(Page):
    def __init__(self, parent:GameWindow):
        super().__init__(parent, 0, 0, 0, 0)
        self.batch = graphics.Batch()
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
    
    def render(self):
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
    
    def on_input(self):
        username = ''.join(self.username.inputseq)
        password = ''.join(self.password.inputseq)
        match1 = bool(re.match(self.userregx, username))
        match2 = bool(re.match(self.passregx, password))
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
        print("Called")
        self.parent.set_page(waitingPage)



# img = image.load(os.path.join("assets", "loading.bmp"))
width = 1000
ratio = videoCip.h/videoCip.w
window = GameWindow(width, int(ratio*width), vsync=False, fullscreen=False)

page = WelcomePage(window, 0)
waitingPage = WaitPage(window, None)
loginPage = LoginPage(window)
page.add()
waitingPage.add()
loginPage.add()
# window.set_fullscreen(True)

# button = Button("Hello", page,page.width/2 ,page.height/2, _anchor=Anchor.ANCHOR_CENTER)
# label = Text("Connecting to server", page, 0, 0, _anchor=Anchor.ANCHOR_LEFT)
# button2 = Button("Hello", page,, _anchor=Anchor.ANCHOR_CENTER)
app.run()