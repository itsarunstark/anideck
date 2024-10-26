from pyglet import window, shapes, graphics, clock, image, sprite, app, gl, text
from gui.page import Page
from gui.color import Color
from gamewindow import GameWindow
from gui.event import Event, EventType
import math
from waitpage import WaitPage

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