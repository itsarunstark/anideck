from pyglet import *
from pyglet.window import Window
import math
from typing import List,Union,Iterable, Callable, Dict, Any
import socket
import os
from enum import Enum
import glob
from moviepy.editor import VideoFileClip

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






class Anchor:
    ANCHOR_CENTER = 0x01
    ANCHOR_LEFT = 0x02
    ANCHOR_RIGHT = 0x04
    ANCHOR_TOP = 0x08
    ANCHOR_BOTTOM = 0x10
    ANCHOR_HORIZONTAL = 0x20
    ANCHOR_VERTICAL = 0x40

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

class BoundBox:
    def __init__(self, parent, x:float, y:float, w:float, h:float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.parent = parent
        self.order = self.parent.order
    def contains(self, x, y):
        # print(self.y, self.y + self.h)
        return ((self.y <=y < self.y + self.h) and (self.x <= x < self.x + self.w))

    def get_area(self):
        return abs((self.w - self.x)*(self.h - self.y))
    
    def __repr__(self):
        return "<BoundBox::[{} {} {} {}]>".format(self.x, self.y, self.w, self.h)
    

class BoundCapsule(BoundBox):
    def __init__(self, parent, x1:float, y1:float, x2:float, y2:float, r:float):
        super().__init__(parent, x1, y1, x2, y2)
        self.r = r
    
    def contains(self, x, y):
        ba2 = (self.x - self.w)**2 + (self.y - self.h)**2
        ba = (ba2)**(0.5)
        h = ((x - self.x)*(self.w - self.x) + (y - self.y)*(self.h - self.y))/ba2
        h = min(1, max(0, h))
        d = (x - self.x) - h*(self.w - self.x), (y - self.y) - h*(self.h - self.y)
        s = (d[0]*d[0] + d[1]*d[1])**(0.5)
        return s < self.r
        

class Color:
    COLOR_BLACK = (0, 0, 0, 255)
    COLOR_WHITE = (255, 255, 255, 255)
    COLOR_BLUE = (0, 12, 245, 255)
    COLOR_RED = (255, 45, 13, 255)

class GameWindow:
    pass

def get_ip_address():
    s = socket.socket()
    s.connect(('1.1.1.1', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def get_text_dimensions(text_, font_name='Arial', font_size=16):
    # Create a Label for measuring
    label = text.Label(
        text_,
        font_name=font_name,
        font_size=font_size
    )
    return label.width, label.height

# ip_address = get_ip_address()

class Page(shapes.Rectangle):
    def __init__(self,
                win:GameWindow, # type: ignore
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
        self.update_queue:Dict[Widget,Callable[[float],Any]] = {

        }
        for attrib in self.__dir__():
            if not isinstance(self.__getattribute__(attrib), Callable) and attrib in kwargs:
                self.__setattr__(attrib, kwargs[attrib])


    def add(self):
        self.parent.add_page(self)
        self.group = shapes.Group(order=self.order)
    
    def catch_event(self, event:Event):
        # print("Catched event", event)
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
                print(self.widgets)
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

@classmethod
def update_img(self, dt):
    super().update(dt)
    self.img.blit(0,0)
    print("yeah working")

        


        

class Widget:
    def __init__(self, parent:Union[Page], x, y, anchor):
        
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
        self.boundbox:BoundCapsule = None
    
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
        

class Text(Widget):
    def __init__(
            self,
            text_:str,
            parent:Union[Page],
            x:float,
            y:float,
            _anchor=Anchor.ANCHOR_CENTER,
            font_size=16,
            font_name="JetBrains Mono",
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
        print(self.y, self.anchor_y)
    
    def widget_resolve(self):
        super().widget_resolve()
        self._label.x = self.anchor_x
        self._label.y = self.anchor_y
        self.boundbox.x = self.anchor_x 
        self.boundbox.y = self.anchor_y



class Button(Widget):
    def __init__(
            self, 
            text_:str, 
            parent:Union[Page], 
            x:float, 
            y:float, 
            _anchor=Anchor.ANCHOR_CENTER,
            font_size=16,
            font_name="JetBrains Mono",
            font_color=Color.COLOR_WHITE,
            background_color=Color.COLOR_RED,
            background_border=0,
            background_border_color=Color.COLOR_RED,
            padding_top=5,
            padding_left=10,
            padding_bottom=5,
            padding_right=10,
            center=False
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
        print("text::", self.w, self.h, self._label.content_height)
        print("BoundBox::", self.boundbox)
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
        self.parent.update_queue[self] = self.update_this
        print("print::", self._background_color)
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
        print(self.boundbox)

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
    def disable(self):
        return self.disabled

    @disable.setter
    def disable(self, value:bool):
        self.batch = self.batch if not value else None
        self._label.batch = self.batch
        self.disabled = value
    
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
        print(self.boundbox, event)
        inactive_color = self._background_color
        active_color = Color.COLOR_BLACK
        click_color = Color.COLOR_WHITE
        if (event.event_type == EventType.MOUSEENTER):
            self._background_rect.color = active_color
        if (event.event_type == EventType.MOUSEDOWN):
            self._background_rect.color = click_color
        if (event.event_type == EventType.MOUSELEAVE):
            self._background_rect.color = inactive_color
        if (event.event_type == EventType.MOUSEUP):
            self._background_rect.color = active_color
            
        # return super().catch_event(event)
    def update_this(self, dt):
        ...
    
        
        

class GameWindow(window.Window):
    def __init__(self, width, height):
        super().__init__(width=width, height=height, resizable=True)
        clock.schedule_interval(self.update, 1 / 60)
        self._network_ip = '127.0.0.1'
        self.pages:Union[List[Page], Iterable[Page]] = []
        self.batch = graphics.Batch()
        self.order = 0
        self.current_page = None
        self.loading_page = Page(self, 0, 0, 0, 0, color=Color.COLOR_BLUE)

    @property
    def network_ip(self)->str:
        return self._network_ip
    
    @network_ip.setter
    def network_ip(self, value:str):
        self._network_ip = value
    
    def on_resize(self, width, height) -> None:
        super().on_resize(width, height)
        self.current_page.resize(width, height)
        # print(self.width, self.height, width, height)
        # return super().on_resize(width, height)
        ...
    
    def set_page(self, page:Page):
        self.current_page = page

    def update(self, dt):
        if (self.current_page) : self.current_page.update(dt)
    
    def on_draw(self):
        self.clear()
        # print(button._label.content_height, button._label.content_width)
        # self.current_page.render()
        self.current_page.render()
    
    def add_page(self, page:Page):
        self.pages.append(page)
        if self.current_page is None:
            self.current_page = page
    
    def on_mouse_enter(self, x: int, y: int) -> None:
        event = Event(
            eventtype=EventType.MOUSEENTER,
            x=x,
            y=y
        )
        self.current_page.catch_event(event)
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        event = Event(
            eventtype=EventType.MOUSEDOWN,
            x=x,
            y=y,
            key=button,
            modifier=modifiers
        )
        self.current_page.catch_event(event)
    
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        event = Event(
            eventtype=EventType.MOUSEUP,
            x=x,
            y=y,
            key=button,
            modifier=modifiers
        )
        self.current_page.catch_event(event)
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        event = Event(
            eventtype=EventType.MOUSEMOTION,
            x=x,
            y=y,
            dx=dx,
            dy=dy
        )
        self.current_page.catch_event(event)


print(Color.COLOR_BLACK)


class WelcomePage(Page):
    def __init__(self, win, welcome_img:image.ImageData, *args, **kwargs):

        super().__init__(win, 0, 0, 0, 0, 0, *args, **kwargs)
        self.batch=graphics.Batch()
        self.video_clip = VideoFileClip('assets/loading.mp4')
        self.counter = 0
        self.group = graphics.Group(self.order-1)
        frame = self.video_clip.get_frame(self.counter)
        self.img = image.ImageData(self.video_clip.w, self.video_clip.h, 'RGB', frame.tobytes())
        self.imgsprite = sprite.Sprite(self.img, x=0, y=0, batch=self.batch, group=self.group)
        self.imgsprite.scale_x = self.height / self.img.height
        self.imgsprite.scale_y = self.height / self.img.height
        self.color = (0, 0, 0, 50)
        self.runtime = 0.0
        # self.loader = shapes.Arc(x=400, y=300, radius=100, angle=1, color=(255, 0, 0), batch=self.batch, group=graphics.Group(self.order+10), thickness=3)
        self.message = text.Label(
            text="Connecting to server",
            font_name="Noto Sans",
            font_size=24,
            x=self.width//2,
            y=self.height//2,
            color=Color.COLOR_WHITE,
            batch=self.batch,
            group=graphics.Group(self.order+1),
            anchor_x='center',
            anchor_y='center'
        )

        self.progress_bar = Progressbar(self, self.width/2, self.height/5, 100, 10)
        self.progress_bar.bar.opacity = 123
        

    def update(self, dt):
        self.runtime += dt
        self.progress_bar.x = self.width/2 + math.sin(math.pi*self.runtime*60.0/180)*300
        self.progress_bar.bar.opacity = int(255*(1-abs(math.sin(math.pi*self.runtime*60.0/180))))
        self.progress_bar.widget_resolve()
        # print("updating")
        return super().update(dt)

    def loadfunction(self,x):
        return math.sin(x)


    def resize(self, width, height):
        self.width = width
        self.height = height
        self.imgsprite.scale_x = width/self.img.width
        self.imgsprite.scale_y = width/self.img.width
        new_width = width
        new_height = self.img.height * (width/self.img.width)
        self.imgsprite.x = (self.width - new_width)//2
        self.imgsprite.y = (self.height - new_height)//2
        self.message.x = width//2
        self.message.y = height//2
        self.progress_bar.x = width/2
        self.progress_bar.y = height/5
        self.progress_bar.widget_resolve()
    
    def render(self):
        self.counter += 1/self.video_clip.fps
        if (self.counter > self.video_clip.duration):self.counter = 0
        frame = self.video_clip.get_frame(self.counter)
        self.img = image.ImageData(self.video_clip.w, self.video_clip.h, 'RGB', frame, pitch=-self.video_clip.w*3)
        self.imgsprite.image = self.img
        self.batch.draw()
        # print("rendering")

    
    



img = image.load(os.path.join("assets", "loading.bmp"))
width = 1400
ratio = img.height/img.width
window = GameWindow(width, int(width*ratio))

# resized_image = image.ImageData(
#     window.width//2, 
#     window.height//2,
#     'RGB', 
#     img.get_image_data().get_data('RGB', img.width * 3), 
#     pitch=img.width * 3
# )

page = WelcomePage(window, img)
page.add()
# button = Button("Hello", page,page.width/2 ,page.height/2, _anchor=Anchor.ANCHOR_CENTER)
# label = Text("Connecting to server", page, 0, 0, _anchor=Anchor.ANCHOR_LEFT)
# button2 = Button("Hello", page,, _anchor=Anchor.ANCHOR_CENTER)
app.run()