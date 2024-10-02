from pyglet import shapes, graphics
from enum import Enum
from .anchor import Anchor
from typing import List, Callable, Dict, Any, Union
from pyglet.window import Window
from .widget import Widget
from .event import Event, EventType

class Page(shapes.Rectangle):
    def __init__(self,
                win:Window, # type: ignore
                margin_t:int = 0,
                margin_l:int = 0,
                margin_b:int = 0,
                margin_r:int = 0,
                batch:graphics.Batch = None
                , *args, **kwargs
        ):
        super().__init__(
            margin_l,
            margin_t, 
            win.width - (margin_l+margin_r),
            win.height - (margin_t+margin_b)
        )
    
        self.parent:Window = win
        self.order = self.parent.order+10
        self.batch = graphics.Batch()
        self.widgets: List[Widget] = []
        self.active_widget:Widget = None
        self._focused_widget:Widget = None
        self.update_queue:Dict[Widget,Callable[[float],Any]] = {

        }
        for attrib in self.__dir__():
            if not isinstance(self.__getattribute__(attrib), Callable) and attrib in kwargs:
                self.__setattr__(attrib, kwargs[attrib])


    def add(self):
        self.parent.add_page(self)
        self.group = shapes.Group(order=self.order)
    
    @property
    def focused_widget(self):
        return self._focused_widget
    
    @focused_widget.setter
    def focused_widget(self, widget:Union[Widget,None]):
        if (self.focused_widget):
            self.focused_widget.set_focus(False)
        self._focused_widget = widget
        if (widget): widget.set_focus(True)
        # print(widget)
    
    def catch_event(self, event:Event):
        # for widget in self.focused_widgets:
        #     widget.catch_event(event)
        # print("Catched event", event)
        if ((self.focused_widget is not None) and (self.focused_widget is not self.active_widget)): self.focused_widget.catch_event(event)
        if event.event_type in [EventType.MOUSEENTER, EventType.MOUSELEAVE, EventType.MOUSEMOTION]:
            if (self.active_widget and (not self.active_widget.disabled)):
                
                if (self.active_widget.boundbox.contains(event.x, event.y)):
                    self.throw_event(event)
                else:
                    self.throw_event(Event(
                        EventType.MOUSELEAVE,
                        x=event.x,
                        y=event.y
                    ))
                    self.active_widget = None
            else:
                # print(self.widgets)
                for widget in self.widgets:
                    if ((not widget.disabled) and widget.boundbox.contains(event.x, event.y)):
                        self.active_widget = widget
                        self.throw_event(Event(
                            EventType.MOUSEENTER,
                            x=event.x,
                            y=event.y
                        ))
                        break
        else:
            self.throw_event(event)
    
    def throw_event(self, event:Event):
        if (self.active_widget):
            self.active_widget.catch_event(event)
    
    def render(self):
        self.batch.draw()
    
    def update(self, dt):
        for widget, method in self.update_queue.items():
            if not (widget.disabled) : method(dt)
    
    def resize(self, width, height):
        self.width = width
        self.height = height
        # print("updating")