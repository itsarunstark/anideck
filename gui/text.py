from .widget import Widget
from typing import Union
from .page import Page
from .anchor import Anchor
from .color import Color
from pyglet import text, graphics
from .boundbox import BoundBox

class Text(Widget):
    def __init__(
            self,
            text_:str,
            parent:Union[Page],
            x:float,
            y:float,
            _anchor=Anchor.ANCHOR_CENTER,
            font_size=16,
            font_name=None,
            font_color=Color.COLOR_WHITE,
            align="left",
            batch=None,
    ):

        print(y)
        super().__init__(parent, x, y, _anchor)
        print("info::", self.y, self.parent.y)
        self.anchor = _anchor
        self._align = align
        self.batch = batch if batch else parent.batch
        self.anchor_y = self.y
        self.anchor_x = self.x
        self._label = text.Label(
            text_, 
            x=self.anchor_x, 
            y=self.anchor_y,
            batch=self.batch, 
            font_name=font_name, 
            font_size=font_size, 
            color=font_color,
            group=graphics.Group(self.order)
        )

        self._w = self._label.content_width
        self._h = self._label.content_height
        self.boundbox = BoundBox(self, self.x, self.y, self.w, self.h)
        self.widget_resolve()
        # print(self.y, self.anchor_y)
    
    def widget_resolve(self):
        super().widget_resolve()
        self._label.x = self.anchor_x
        self._label.y = self.anchor_y
        self.boundbox.x = self.anchor_x 
        self.boundbox.y = self.anchor_y

