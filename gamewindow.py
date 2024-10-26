from pyglet import window, shapes, graphics, clock, image, sprite, app, gl
from pyglet.window import key
from gui.page import Page
from client import GameUser, GameMsg
from network.cookiejar import Cookie, CookieOpt, CookieManager
from client import Client, ClientDB
from gui.color import Color
from gui.event import Event, EventType

FPS = 60
class GameWindow(window.Window):
    def __init__(self, width, height, gameServer:Client, clientDB:ClientDB, *args, **kwargs):
        super().__init__(width, height, "GameWindow", resizable=True, *args, **kwargs)
        self.fps = FPS
        self.gameUser = GameUser(None, gameServer, clientDB)
        clock.schedule_interval(self.update, 1 / self.fps)
        self.current_user = None
        self._network_ip = '127.0.0.1'
        self.videoClip = None
        self.gameServer:GameUser = None
        self.clientDB:ClientDB = None
        # self.pages:Union[List[Page], Iterable[Page]] = []
        self.batch = graphics.Batch()
        self.order = 0
        self.counter = 0
        self.current_page = None
        self.loading_page = Page(self, 0, 0, 0, 0, color=Color.COLOR_BLUE)
        self._fullscreen = False
        # print(self.gameServer.connect_to_server())
        # self.gameEngine = 


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
        self.current_page.resize(self.width, self.height)

    def update(self, dt):
        if (self.current_page) : self.current_page.update(dt)
    
    def on_draw(self):
        self.clear()
        # print(button._label.content_height, button._label.content_width)
        # self.current_page.render()
        self.current_page.render()
    
    def on_key_press(self, symbol:int, modifiers:int):
        super().on_key_press(symbol, modifiers)
        if (symbol == key.F11):
            self.set_fullscreen(not self.fullscreen)
        event = Event(EventType.KEYDOWN, 0, 0, symbol, modifiers, 0, 0)
        self.current_page.catch_event(event)
    
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        # super().on_key_release(symbol, modifiers) mvc
        event = Event(EventType.KEYUP, 0, 0, symbol, modifiers)
        self.current_page.catch_event(event)
    
    def add_page(self, page:Page):
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