from .color import Color
from .widget import Widget
from .page import Page
from typing import Union, Callable
from enum import Enum
from .anchor import Anchor
from .boundbox import BoundBox, BoundCapsule
from pyglet import graphics, shapes

class Progressbar(Widget):
    def __init__(self,parent:Union[Page], x:float=0, y:float=0,w:float=100, r:float=4, batch=None, anchor:Enum = Anchor.ANCHOR_CENTER):
        super().__init__(parent, x, y, anchor)
        self.background_color = Color.COLOR_RED
        self.foreground_color = Color.COLOR_WHITE
        self.w = w
        self.h = r
        self.batch = batch if batch else parent.batch
        self.progress = 1
        self.boundbox = BoundCapsule(self, self.x, self.y, self.x+self.w, self.y, self.h/2)
        self.bar = shapes.RoundedRectangle(
            self.x,
            self.y,
            self.w,
            self.h,
            self.h/2,
            color=Color.COLOR_WHITE,
            batch=self.batch,
            group=graphics.Group(self.order+1)
        )

        self.widget_resolve()

    def widget_resolve(self):
        super().widget_resolve()
        self.bar.x = self.anchor_x
        self.bar.y = self.anchor_y
        self.boundbox.x = self.anchor_x
        self.boundbox.y = self.anchor_y + self.h/2
        self.boundbox.w = self.anchor_x + self.w
        self.boundbox.h = self.anchor_y + self.h/2
        self.boundbox.r = self.h/2
        