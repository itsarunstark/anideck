from typing import Union,Callable
from .anchor import Anchor
from .widget import Widget
from .page import Page
from pyglet import graphics, shapes, text
from pyglet.window import key
from .event import Event, EventType
from .color import Color
from .boundbox import BoundBox
import math

class InputBox(Widget):
    def __init__(self,parent:Union[Page], x, y, hint, maxchars:int=26):
        self.text_label = None
        self.text_background = None
        self.readonly = False
        self.inputtext = "\0"
        self._focused = False
        self.maxchars = maxchars
        self.maskfunction = lambda x:x
        super().__init__(parent, x, y, Anchor.ANCHOR_CENTER)
        self.text = "  "*maxchars
        self.inputseq = []
        self.text_label = text.Label(
            x=self._x, 
            y=self._y,
            text=self.text, 
            anchor_x='center', 
            anchor_y='center', 
            batch=self.batch,
            group=graphics.Group(self.order+2),
            font_name="Consolas"
        )
        self.cursor = shapes.Rectangle(0,0,0,0, color=Color.COLOR_WHITE, group=self.text_label.group, batch=self.batch)
        self._width = self.text_label.content_width
        self._height = self.text_label.content_height

        
        self.x = x
        self.y = y
        self._padding_left = 10
        self._padding_right = 10
        self._padding_top = 10
        self._padding_bottom = 10
        self.hint = hint
        self.counter = 0
        self.blinkdelay = 0.1
        self.oninput = lambda : None
        self.active_color = Color.COLOR_GREEN
        self.inactive_color = Color.COLOR_GREY



        self.text_background = shapes.Rectangle(
            self.text_label.x - self._width/2 - self._padding_left,
            self.text_label.y - self._height/2 - self._padding_top,
            self._width + self._padding_left + self._padding_right,
            self._height + self._padding_bottom + self._padding_top,
            (0, 0, 0, 156),
            group=graphics.Group(self.order+1),
            batch=self.batch
        )

        self.batch

        self.boundbox = BoundBox(self, self.x, self.y, self.w, self.h)
        parent.update_queue[self] = self.update_sequence

    



    @property
    def x(self):return self._x

    @x.setter
    def x(self, _x):
        self._x = _x
        self.widget_resolve()

    @property
    def y(self):return self._y
    
    @y.setter
    def y(self, _y):
        self._y = _y
        self.widget_resolve()
    
    def update_sequence(self, dt):
        # print(self.text_label.content_width)
        self.counter += dt
        self.text_label.color = self.active_color if self._focused else self.inactive_color
        self.text_label.text = self.hint
        if not ((self._focused) or self.inputseq.__len__()):
            self.text_label.text = self.hint
        else:
            self.text_label.text = self.inputtext
        if (self._focused):
            # print(self.text_label.content_width)
            self.cursor.width = 7
            self.cursor.height = self._height
            self.cursor.x = self.text_label.x + self.text_label.content_width/2
            self.cursor.y = self.text_label.y - self.text_label.content_height/2
            # print(self.cursor.x, self.cursor.y, self.cursor.width, self.cursor.height)
        self.cursor.visible = (math.floor(self.counter/self.blinkdelay)%2) and self._focused
        
        
        
        
    
    def catch_event(self, event: Event):
        if not self.readonly:
            if (event.event_type == EventType.MOUSEDOWN):
                self.parent.focused_widget = self if not self._focused else None
            
            if (self._focused and event.event_type == EventType.KEYDOWN):
                if (event.key == key.BACKSPACE):
                    if self.inputseq.__len__():
                        self.inputseq.pop()
                elif (key._0 <= event.key <= key._9) and len(self.inputseq) < self.maxchars:
                    symbol = chr(event.key)
                    self.inputseq.append(symbol)
                elif (key.A <= event.key <= key.NUM_9) and len(self.inputseq) < self.maxchars:
                    self.inputseq.append(chr(event.key - (event.modifiers & (key.MOD_SHIFT))*32))
                self.inputtext = '\0'+''.join(map(self.maskfunction, self.inputseq))
                self.oninput()
                # print(self.inputseq)
        
        
    


    def widget_resolve(self):
        if (self.text_label):
            self.text_label.x = self.x
            self.text_label.y = self.y
        if (self.text_background) and (self.text_label):
            self.text_background.x = self.text_label.x - self._width/2 - self._padding_left
            self.text_background.y = self.text_label.y - self._height/2 - self._padding_top
            self.text_background.width = self._width + self._padding_left + self._padding_right
            self.text_background.height = self._height + self._padding_top + self._padding_bottom
            self.boundbox.x = self.text_background.x
            self.boundbox.y = self.text_background.y
            self.boundbox.w = self.text_background.width
            self.boundbox.h = self.text_background.height
    
        
