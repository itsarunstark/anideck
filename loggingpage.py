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


class LoggingPage(Page):
    def __init__(self, parent:GameWindow):
        super().__init__(parent, 0, 0, 0, 0)
        self.parent:GameWindow = parent
        self.video_clip = self.parent.videoClip
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