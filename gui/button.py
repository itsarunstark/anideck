from .page import Page
from .anchor import Anchor
from .color import Color
from typing import Union, Callable
from .widget import Widget
from pyglet import text, graphics, shapes
from .event import Event, EventType
from .boundbox import BoundBox, BoundCapsule

class Button(Widget):
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
            background_color=Color.COLOR_BLACK,
            background_border=0,
            background_border_color=Color.COLOR_RED,
            padding_top=5,
            padding_left=10,
            padding_bottom=5,
            padding_right=10,
            center=False,
            batch:graphics.Batch=None
            ):
        # print(_anchor)
        # self.order = parent.group.order + 10
        self._anchor = _anchor
        super().__init__(parent, x, y, _anchor)
        self._label = text.Label(
            text_, 
            x=self.anchor_x, 
            y=self.anchor_y,
            batch=self.batch, 
            font_name=font_name, 
            font_size=font_size, 
            color=font_color,
            group =graphics.Group(self.order),
            anchor_y="bottom"
        )
        self.anchor_x = x
        self.anchor_y = y
        self.old_batch = self.batch
        # print("text::", self.w, self.h, self._label.content_height)
        # print("BoundBox::", self.boundbox)
        self.w = self._label.content_width + padding_left + padding_right
        self.h = self._label.content_height + padding_top + padding_bottom
        self._text = text_
        self._font_name = font_name
        self._font_size = font_size
        self._font_color = font_color
        self._background_color = background_color
        self._background_border = background_border
        self._background_border_color = background_border_color
        self._padding_top = padding_top
        self._padding_left = padding_left
        self._padding_bottom = padding_bottom
        self._padding_right = padding_right
        self._active_color = Color.COLOR_RED
        self._click_color = Color.COLOR_WHITE
        self._callerfun = lambda: None
        self.active = True
        self.parent.update_queue[self] = self.update_this
        # print("print::", self._background_color)
        self._background_rect = shapes.Rectangle(
            x=self.anchor_x,
            y=self.anchor_y,
            width=self.w,
            height=self.h,
            color=self.background_color, 
            batch=self.batch,
            group=graphics.Group(self.order)
        )
        self.boundbox = BoundBox(self, self.anchor_x, self.anchor_y, self.w, self.h)
        self.widget_resolve()
        # print(self.boundbox)

    @property
    def font_name(self):
        return self._font_name
    
    @font_name.setter
    def font_name(self, value:str):
        self._font_name = value
        self._label.font_name = value
    
    @property
    def font_size(self):
        return self._font_size
    
    @font_size.setter
    def font_size(self, value:int):
        self._font_size = value
        self._label.font_size = value
    
    @property
    def font_color(self):
        return self._font_color
    
    @font_color.setter
    def font_color(self, value:Color):
        self._font_color = value
        self._label.color = value
    
    @property
    def background_color(self):
        return self._background_color
    
    @background_color.setter
    def background_color(self, value:Color):
        self._background_color = value
    
    @property
    def background_border(self):
        return self._background_border
    
    @background_border.setter
    def background_border(self, value:int):
        self._background_border = value
    
    @property
    def background_border_color(self):
        return self._background_border_color
    
    @background_border_color.setter
    def background_border_color(self, value:Color):
        self._background_border_color = value
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value:str):
        self._text = value
    
    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value:bool):
        self._disabled = value
        self.active = value
    
    @property
    def anchor(self):
        return self._anchor
    
    @anchor.setter
    def anchor(self, value):
        self._anchor = value
        self.widget_resolve()
    

    
    def widget_resolve(self):
        super().widget_resolve()
        self._label.x = self.anchor_x + self._padding_left
        self._label.y = self.anchor_y + self._padding_bottom
        self._background_rect.x = self.anchor_x
        self._background_rect.y = self.anchor_y
        self.boundbox.x = self.anchor_x
        self.boundbox.y = self.anchor_y
    
    def catch_event(self, event: Event):
        # print(self.boundbox, event)
        inactive_color = self._background_color
        active_color = self._active_color
        click_color = self._click_color
        if self.active:
            if (event.event_type == EventType.MOUSEENTER):
                self._background_rect.color = active_color
            if (event.event_type == EventType.MOUSEDOWN):
                self._background_rect.color = click_color
                self._callerfun()
            if (event.event_type == EventType.MOUSELEAVE):
                self._background_rect.color = inactive_color
            if (event.event_type == EventType.MOUSEUP):
                self._background_rect.color = active_color
            
            
        # return super().catch_event(event)
    def update_this(self, dt):
        ...
    
    def onClick(self, callfn:Callable):
        self._callerfun = callfn
    
class GameButton(Button):
    def widget_resolve(self):
        super().widget_resolve()
        self.background_color = Color.COLOR_BLACK
        self._active_color = Color.COLOR_CRIMSON_RED
        self._click_color = Color.COLOR_DARK_RED