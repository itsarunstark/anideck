from pyglet import window, shapes, graphics, clock, image, sprite, app, gl, text
from pyglet.window import key
from gui.page import Page
from gui.color import Color
from gamewindow import GameWindow
from gui.event import Event, EventType
from schedular import Job, Priority
from gui.progressbar import Progressbar
from gui.button import Button, GameButton
from gui.inputbox import InputBox
from gui.anchor import Anchor
from network import PROTOCOLS, GameMsg
import loginpage

class GuildPage(Page):
    def __init__(self, parent:GameWindow):
        super().__init__(parent, 0, 0, 0, 0)
        self.parent:GameWindow = parent
        # self.joingameBtn = GameButton("Join Game", self, 0, 0)
        self.createGame = GameButton("Play Game", self, 0, 0, batch=self.batch)
        self.settings = GameButton("Settings", self, 0, 0, batch=self.batch)
        self.friends = GameButton("Friends", self, 0, 0, batch=self.batch)
        self.inventory = GameButton("Inventory", self, 0, 0,  batch=self.batch)
        self.logoutBtn = GameButton("Logout", self, x=0, y=0, batch=self.batch)
        self.color = Color.COLOR_CRIMSON_RED
        self.logoutBtn.onClick(self.logout)
        self.gamestatusmsg = "This txt should be visible"
        self.gamestatusmsgchanged = 0
        self.gamemsg = text.Label(self.gamestatusmsg, 0, self.width, anchor_y='top',font_size=12, batch=self.batch)
        self.switchToPage = 0

    def resize(self, width, height):
        super().resize(width, height)
        self.createGame.x = width/3
        self.friends.x = 2*width/3
        self.inventory.x = width/3
        self.settings.x = 2*width/3
        self.createGame.y = 2*height/3
        self.friends.y = 2*height/3
        self.inventory.y = height/3
        self.settings.y = height/3
        self.logoutBtn.x = self.logoutBtn.w/2
        self.logoutBtn.y = self.logoutBtn.h/2
        self.logoutBtn.widget_resolve()
        self.createGame.widget_resolve()
        self.friends.widget_resolve()
        self.inventory.widget_resolve()
        self.settings.widget_resolve()
        self.joinBatchJob = Job(self.createBatch)
        self.joinBatchJob.callback_function = self.onGameJoin
        self.createGame.onClick(self.onPlay)
        self.gamemsg.y = self.height
        

    def onPlay(self):
        self.parent.schedular.queueJob(self.joinBatchJob, Priority.PRIORITY_HIGH)
    
    def createBatch(self):
        user_data = self.parent.current_user
        return self.parent.gameUser.createBatch(user_data['cookie'])
    
    def logout(self):
        self.parent.clientDB.make_default_user(0)
        self.parent.set_page(loginpage.LoginPage(self.parent))
    
    def onGameJoin(self, job:Job):
        results = job.result
        print(results)
        if (results[0] == PROTOCOLS.PROTO_ACK):
            if (results[1] == GameMsg.MSG_BATCH_QUEUED):
                self.switchToPage = 1
                self.gamestatusmsg = results[2].decode()
    
    def update(self, dt):
        super().update(dt)
        if (self.switchToPage):
            self.parent.set_page(BatchWaitPage(self.parent, self.gamestatusmsg))

class BatchWaitPage(Page):
    def __init__(self, parent:GameWindow, initalMessage:str="looking for players"):
        super().__init__(parent, 0, 0, 0, 0)
        self.parent:GameWindow = parent
        self.color = Color.COLOR_CRIMSON_RED
        self.gamemsg = initalMessage
        self.gameLabel = text.Label(self.gamemsg, self.width/2, self.height/2, anchor_x='center', anchor_y='center')
        self.gameLabel.batch = self.batch
        self.progress = shapes.RoundedRectangle(0, 0, 100, 10, 5, color=Color.COLOR_WHITE, batch=self.batch)
        self.total_players = 1
        self.update_remaining = 0
        self.timeit = 1
        self.timeout = self.parent.fps*180 #change this 180 to some n seconds to get timeout
        self.update_jb = Job(self.fetch_updates)
        self.timemap = "timeout : %02d:%02d"
        self.statustext = text.Label(
            "Looking for players.", 
            self.width/2, 
            self.gameLabel.y - 50, 
            batch=self.batch, 
            font_size=12,
            anchor_x='center',
            anchor_y='center'
        )
        self.timetext = text.Label(
            self.timemap, self.width/2, self.statustext.y - 50, anchor_x='center', anchor_y='center', batch=self.batch, font_size=10
        )
       

    def fetch_updates(self):
        PROTO, MSG, DATA = self.parent.gameUser.getQueueLength()
        print(DATA)
        if (PROTO == PROTOCOLS.PROTO_ACK and MSG == GameMsg.MSG_QUEUE_LENGTH):
            self.total_players = DATA

    def resize(self, width:int, height:int):
        super().resize(width, height)
        self.gameLabel.x = self.width/2
        self.gameLabel.y = self.height/2
        self.statustext.x = self.width/2
        self.statustext.y = self.gameLabel.y - 50
        self.timetext.x = self.width/2
        self.timetext.y = self.statustext.y - 50
    
    def render(self):
        super().render()
    
    def update(self, dt):
        self.timeit += 1
        if (self.timeit > self.timeout):
            status = self.parent.gameUser.withdrawQueue()
            while (not status):
                status = self.parent.gameUser.withdrawQueue()
            page = GuildPage(self.parent)
            page.gamemsg.text = "Client::DEC_TIMEOUT::Previous session was timed-out"
            self.parent.set_page(page)
        if (self.timeit%60 == 0):
            self.parent.schedular.queueJob(self.update_jb, Priority.PRIORITY_LOW)
        if (self.total_players != self.update_remaining):
            self.update_remaining = self.total_players
            self.statustext.text = "Remaining players {}/{}".format(4-self.total_players, 4)
        self.timetext.text = self.timemap%((self.timeout - self.timeit)//3600, ((self.timeout - self.timeit)//60)%60)        
