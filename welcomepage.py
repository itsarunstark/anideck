from pyglet import window, shapes, graphics, clock, image, sprite, app, gl, text
from gui.page import Page
from gui.color import Color
from gamewindow import GameWindow
from gui.event import Event, EventType
from schedular import Job, Priority
from gui.progressbar import Progressbar
from gui.button import Button
import math
from tools import *
from registerpage import RegisterPage
from loginpage import LoginPage


class WelcomePage(Page):
    def __init__(self, window:GameWindow, counter, *args, **kwargs):
        # self.batch = graphics.Batch()
        self.parent = window
        super().__init__(window, 0, 0, 0, 0, *args, **kwargs)
        self.batch = graphics.Batch()
        self.color = Color.COLOR_CRIMSON_RED
        self.video_clip = self.parent.videoClip
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

