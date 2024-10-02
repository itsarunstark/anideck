from enum import Enum

class EventType(Enum):
    NULL = 0
    KEYDOWN = 1
    KEYUP = 2
    MOUSEUP = 3
    MOUSEDOWN = 4
    MOUSEMOTION = 5
    MOUSEWHEEL = 6
    MOUSEENTER = 7
    MOUSELEAVE = 8

class Event:
    def __init__(self, eventtype:EventType, x=0, y=0, key=0, modifier=0, dx=0, dy=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.event_type = eventtype
        self.key = key
        self.modifiers = modifier
        self.active_widget = None
    
    def getKey(self):
        return self.key

    def getModifiers(self):
        return self.modifiers
    
    def __repr__(self):
        return "<Event::{} x:{} y:{} key:{} modifiers:{}>".format(
            self.event_type.name,
            self.x, 
            self.y, 
            self.key, 
            self.modifiers
        )
