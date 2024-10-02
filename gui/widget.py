from .boundbox import BoundBox, BoundCapsule
from .anchor import Anchor
from typing import Union, Callable
# from .page import Page
from .event import EventType, Event

class Widget:
    def __init__(self, parent, x, y, anchor):
        
        self._x = 0
        self._y = 0
        self._w = 0
        self._h = 0
        self._anchor = Anchor.ANCHOR_CENTER
        self.w = self._h
        self.h = self._w
        self.x = x + parent.x
        self.y = y + parent.y
        self._parent = parent
        self.parent = parent
        self.order = self.parent.order + 10
        self._anchor_x = 0
        self._anchor_y = 0
        self._disabled = False
        self.batch = self.parent.batch
        self.boundbox:BoundBox = None
        self._focused = False
    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, _parent):
        self._parent.widgets.append(self)
        self._parent = _parent

    def catch_event(self, event:Event):
        print("Not implemented yet")
    
    def throw_event(self, event:Event):
        print("Not yet implemented yet.")
    
    def render(self):
        pass

    def set_focus(self, focused):
        self._focused = focused

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value:bool):
        self.batch = self.batch if value else None
        self._disabled = value
    
    @property
    def anchor(self):
        return self._anchor

    @anchor.setter
    def anchor(self, value):
        self._anchor = value
    
    @property
    def anchor_x(self):
        return self._anchor_x
    
    @anchor_x.setter
    def anchor_x(self, value):
        self._anchor_x = value
    
    @property
    def anchor_y(self):
        return self._anchor_y
    
    @anchor_y.setter
    def anchor_y(self, value):
        self._anchor_y = value
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
    
    @property
    def w(self):
        return self._w
    
    @w.setter
    def w(self, value):
        self._w = value
    
    @property
    def h(self):
        return self._h
    
    @h.setter
    def h(self, value):
        self._h = value
    
    def widget_resolve(self):
        # print(self.anchor)
        if (self.anchor & Anchor.ANCHOR_CENTER):
            self.anchor_x = self.x - self.w/2
            self.anchor_y = self.y - self.h/2

        if (self.anchor & Anchor.ANCHOR_LEFT): self.anchor_x = self.x

        if (self.anchor & Anchor.ANCHOR_RIGHT): self.anchor_x = self.x - self.w

        if (self.anchor & Anchor.ANCHOR_TOP): self.anchor_y = self.y

        if (self.anchor & Anchor.ANCHOR_BOTTOM): self.anchor_y = self.y - self.h

        if (self.anchor & Anchor.ANCHOR_HORIZONTAL): self.anchor_y = self.y - self.h/2

        if (self.anchor & Anchor.ANCHOR_VERTICAL):
            self.x = self.x - self.w/2
