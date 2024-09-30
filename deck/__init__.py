import os
import sys
from types import UnionType
import math
import random
from typing import List,Any, Union
from enum import Enum

#defining sequence
# @code bits : C GG NNNN
# @author : Arun Kumar
# @email : bg47msva@gmail.com

class DeckTools(object):

    @staticmethod
    def shuffle(arr:List[Any], key=lambda x: x, cmp=lambda x, y: x < y)->None:
        i:int = 1
        size:int = len(arr)
        if (size == 0 or size == 1) :return
        while (i < size):
            if (cmp(key(arr[i-1]), key(arr[i])) < 0):
                arr[i-1], arr[i] = arr[i], arr[i-1]
                i -= 2 if (i > 1) else 0
            i += 1
        

class Colors(Enum):
    RED = 0x00
    BLACK = 0x40

    def __or__(self, other:Enum):
        return self.value | other.value
    
    def __and__(self, other:Enum):
        return self.value & other.value

class Groups(Enum):
    SPADE = 0x00|Colors.BLACK.value
    CLUB = 0x10|Colors.BLACK.value
    HEART = 0x20|Colors.RED.value
    DIAMOND = 0x30|Colors.RED.value

    def __or__(self, other:Enum):
        return self.value | other.value
    
    def __and__(self, other:Enum):
        return self.value & other.value

class Cards(Enum):
    ACE = 0x01
    TWO = 0x02
    THREE = 0x03
    FOUR = 0x04
    FIVE = 0x05
    SIX = 0x06
    SEVEN = 0x07
    EIGHT = 0x08
    NINE = 0x09
    TEN = 0x0A
    JACK = 0x0B
    QUEEN = 0x0C
    KING = 0x0D

    def __or__(self, other:Enum):
        return self.value | other.value
    
    def __and__(self, other:Enum):
        return self.value & other.value

class Deck(Enum):
    ACE_OF_SPADE = Cards.ACE|Groups.SPADE
    TWO_OF_SPADE = Cards.TWO|Groups.SPADE
    THREE_OF_SPADE = Cards.THREE|Groups.SPADE
    FOUR_OF_SPADE = Cards.FOUR|Groups.SPADE
    FIVE_OF_SPADE = Cards.FIVE|Groups.SPADE
    SIX_OF_SPADE = Cards.SIX|Groups.SPADE
    SEVEN_OF_SPADE = Cards.SEVEN|Groups.SPADE
    EIGHT_OF_SPADE = Cards.EIGHT|Groups.SPADE
    NINE_OF_SPADE = Cards.NINE|Groups.SPADE
    TEN_OF_SPADE = Cards.TEN|Groups.SPADE
    JACK_OF_SPADE = Cards.JACK|Groups.SPADE
    QUEEN_OF_SPADE = Cards.QUEEN|Groups.SPADE
    KING_OF_SPADE = Cards.KING|Groups.SPADE
    ACE_OF_CLUB = Cards.ACE|Groups.CLUB
    TWO_OF_CLUB = Cards.TWO|Groups.CLUB
    THREE_OF_CLUB = Cards.THREE|Groups.CLUB
    FOUR_OF_CLUB = Cards.FOUR|Groups.CLUB
    FIVE_OF_CLUB = Cards.FIVE|Groups.CLUB
    SIX_OF_CLUB = Cards.SIX|Groups.CLUB
    SEVEN_OF_CLUB = Cards.SEVEN|Groups.CLUB
    EIGHT_OF_CLUB = Cards.EIGHT|Groups.CLUB
    NINE_OF_CLUB = Cards.NINE|Groups.CLUB
    TEN_OF_CLUB = Cards.TEN|Groups.CLUB
    JACK_OF_CLUB = Cards.JACK|Groups.CLUB
    QUEEN_OF_CLUB = Cards.QUEEN|Groups.CLUB
    KING_OF_CLUB = Cards.KING|Groups.CLUB
    ACE_OF_HEART = Cards.ACE|Groups.HEART
    TWO_OF_HEART = Cards.TWO|Groups.HEART
    THREE_OF_HEART = Cards.THREE|Groups.HEART
    FOUR_OF_HEART = Cards.FOUR|Groups.HEART
    FIVE_OF_HEART = Cards.FIVE|Groups.HEART
    SIX_OF_HEART = Cards.SIX|Groups.HEART
    SEVEN_OF_HEART = Cards.SEVEN|Groups.HEART
    EIGHT_OF_HEART = Cards.EIGHT|Groups.HEART
    NINE_OF_HEART = Cards.NINE|Groups.HEART
    TEN_OF_HEART = Cards.TEN|Groups.HEART
    JACK_OF_HEART = Cards.JACK|Groups.HEART
    QUEEN_OF_HEART = Cards.QUEEN|Groups.HEART
    KING_OF_HEART = Cards.KING|Groups.HEART
    ACE_OF_DIAMOND = Cards.ACE|Groups.DIAMOND
    TWO_OF_DIAMOND = Cards.TWO|Groups.DIAMOND
    THREE_OF_DIAMOND = Cards.THREE|Groups.DIAMOND
    FOUR_OF_DIAMOND = Cards.FOUR|Groups.DIAMOND
    FIVE_OF_DIAMOND = Cards.FIVE|Groups.DIAMOND
    SIX_OF_DIAMOND = Cards.SIX|Groups.DIAMOND
    SEVEN_OF_DIAMOND = Cards.SEVEN|Groups.DIAMOND
    EIGHT_OF_DIAMOND = Cards.EIGHT|Groups.DIAMOND
    NINE_OF_DIAMOND = Cards.NINE|Groups.DIAMOND
    TEN_OF_DIAMOND = Cards.TEN|Groups.DIAMOND
    JACK_OF_DIAMOND = Cards.JACK|Groups.DIAMOND
    QUEEN_OF_DIAMOND = Cards.QUEEN|Groups.DIAMOND
    KING_OF_DIAMOND = Cards.KING|Groups.DIAMOND

    def __or__(self, other:Enum):
        return self.value | other.value

    def __and__(self, other:Enum):
        return self.value & other.value
    
    @property
    def color(self):
        return Colors(self.value & 0x40)
    
    @property
    def group(self):
        return Groups(self.value & 0x70)
    
    def __tmpaddxtx(self, other:int)->Enum:
        number = ((self.value & 0x0f) + (other &0x0f)) % 0x0d
        code = self.value & 0xf0
        print(code|number, code, number)
        return Deck(code|number)
    
    def __tmpsubxxs(self, other:int)->Enum:
        number = ((self.value & 0x0f) - (other &0x0f)) % 0x0d
        code = ((self.value & 0x30) - (other & 0x30)) &0x30
        return Deck(code|number)
    
    def __add__(self, other: Union[Enum, int])->Enum:
        if isinstance(other, Enum):return self.__tmpaddxtx(other.value)
        if isinstance(other, int):return self.__tmpaddxtx(other)
        
        raise TypeError("Error : object {} of type {} is not supported for object {} type {} __add__".format(
            other, type(other), self, type(self)
        ))

    def __sub__(self, other: Union[Enum, int])->Enum:
        if isinstance(other, Enum): return self.__tmpsubxxs(other.value)
        if isinstance(other, int): return self.__tmpsubxxs(other)
        raise TypeError("Error : object {} of type {} is not supported for object {} type {} __sub__".format(
            other, type(other), self, type(self)
        ))
    
    def __str__(self)->str:
        return self.name
    
    def __repr__(self) -> str:
        return "card::%s"%(self.name)