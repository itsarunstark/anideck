from deck import Deck,List
from typing import Tuple, Set

class Throw(object):
    pass

class Batch(object):
    
    def __init__(self, playersCount:int=4):
        if (playersCount < 3): raise Exception("Not enough players")
        self.playersCount = playersCount
        self.nPlayers = 0
        self.nActivePlayers = 0
        self.players:List[Player] = []
        self.active_players:List[Player] = []
        self.totalMoves = 0
        self.table = {
            Deck.SIX_OF_CLUB: [Deck.SIX_OF_CLUB, 0, []],
            Deck.SIX_OF_SPADE: [Deck.SIX_OF_SPADE, 0, []],
            Deck.SIX_OF_DIAMOND: [Deck.SIX_OF_DIAMOND,0, []],
            Deck.SIX_OF_HEART: [Deck.SIX_OF_HEART,0, []],
            Deck.SEVEN_OF_CLUB: [Deck.SEVEN_OF_CLUB,0, []],
            Deck.SEVEN_OF_SPADE: [Deck.SEVEN_OF_SPADE,0, []],
            Deck.SEVEN_OF_DIAMOND: [Deck.SEVEN_OF_DIAMOND,0, []],
            Deck.SEVEN_OF_HEART: [Deck.SEVEN_OF_HEART,0, []]
        }

    def push_player(self, player):
        player.playerId = self.nPlayers
        self.players.append(player)
        self.active_players.append(player)
        self.nActivePlayers += 1
        self.nPlayers += 1
    
    def distribute_cards(self):
        if not (self.playersCount == self.nPlayers): raise Exception("Not enough players")
        cards = set(Deck)
        i = 0
        while cards:
            self.players[i].add_card(cards.pop())
            i = (i+1)%len(self.players)
    
    def give_next_move(self, player):
        moves = []
        for required in map(lambda x: x[0],self.table.values()):
            if player.has_card(required):
                moves.append(required)
        print(moves)
            


class Player(object):

    def __init__(self,
                 username=None):
        self.previous_moves:List[int] = []
        self.valid_moves:List[bool]
        self.cards:Set[Deck] = set()
        self.username = username
        self.playerId = 0
        self.totalMoves = 0

    def add_card(self, deck:Deck):
        self.cards.add(deck)
        playerId = 0
        # while deck:

    def has_card(self, deck:Deck)->bool:
        return (deck in self.cards)

    def analyzeValidMoves(self):...
    

    def __repr__(self)->str:
        return "player::%(name)s:%(id)d"%{'name':self.username, 'id':self.playerId}
    
    def __str__(self)->str:
        return "player::%(name)s:%(id)d"%{'name':self.username, 'id':self.playerId}

players = 4


batch = Batch(4)
batch.push_player(Player('itsarunstark'))
batch.push_player(Player('aryandixit'))
batch.push_player(Player('manu'))
batch.push_player(Player('shreya'))
batch.distribute_cards()
players = batch.players
batch.give_next_move(players[0])
