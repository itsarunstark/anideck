from network import CookieOpt
import time
import sqlite3
from typing import Union, List, Dict, Optional, Tuple
import datetime
from network.tools import to_bytes, from_bytes, encode_msg


class Cookie:
    def __init__(
            self, 
            userId:int,
            cookieName:str, 
            cookieValue:str, 
            expires:float=-1.0, 
            created:float=-1.0, 
            cookieId:int=None
        ):
        self._userId = userId
        self._name = cookieName
        self._value = cookieValue
        self._created = created if created > 0 else time.time()
        self._expires = expires if expires > 0 else 10*24*3600+self._created
        self._cookieId = int.from_bytes(
            struct.pack("<d", self.created)[:6], byteorder='big'
        ) if cookieId==None else cookieId

    @property
    def name(self)->str: return self._name
    
    @property
    def value(self)->str: return self._value

    @property
    def expires(self)->float: return self._expires

    @property
    def created(self)->float: return self._created

    @property
    def userId(self)->int: return self._userId

    @property
    def id(self)->int: return self._cookieId

    def expired(self)->bool:
        return time.time() > self.expires
    
    def to_bytes(self)->bytearray:
        bytedata = bytearray()
        bytedata.extend(CookieOpt.COOKIE_START.to_bytes())
        bytedata.extend(CookieOpt.COOKIE_ID.to_bytes())
        bytedata.extend(encode_msg(self.id))
        bytedata.extend(CookieOpt.COOKIE_USER_ID.to_bytes())
        bytedata.extend(encode_msg(self.userId))
        bytedata.extend(CookieOpt.COOKIE_NAME.to_bytes())
        bytedata.extend(encode_msg(self.name))
        bytedata.extend(CookieOpt.COOKIE_VALUE.to_bytes())
        bytedata.extend(encode_msg(self.value))
        bytedata.extend(CookieOpt.COOKIE_CREATED.to_bytes())
        bytedata.extend(encode_msg(self.created))
        bytedata.extend(CookieOpt.COOKIE_EXPIRED.to_bytes())
        bytedata.extend(encode_msg(self.expires))
        bytedata.extend(CookieOpt.COOKIE_END.to_bytes())

        return bytedata
    
    @staticmethod
    def from_bytes(cookieBytes:bytes):
        pass
    
    def __repr__(self):
        # print(self.__dict__)
        return (
            "Cookie::id:%(_cookieId)d, [name:%(_name)s , value:%(_value)s, created:%(_created)f, expires:%(_expires)f, userid:%(_userId)d]"%
            self.__dict__
        )
    
    def __str__(self): return self.__repr__()



class CookieManager:
    def __init__(self, database:sqlite3.Connection):
        self.database = database
        self.cursor = self.database.cursor()
    
    def fetch_existsing_cookie(self, userId:int)->Dict[str, Cookie]:
        self.cursor.execute("SELECT * from Cookies WHERE userId=?", (userId, ))
        cookies:List[Tuple[int,int, str, str, datetime.datetime, datetime.datetime]] = self.cursor.fetchall()
        cookieDict:Dict[str, Cookie] = {}
        for cookie in cookies:
            cookieDict[cookie[2]] = (
                Cookie(cookie[1], cookie[2], cookie[3], cookie[5], cookie[4], cookie[0])
            )
        return cookieDict
    
    def fetch_cookie(self, userId:int, cookieName:str)->Optional[Cookie]:
        self.cursor.execute("SELECT * FROM Cookies WHERE userId=? AND cookieName=?", (userId, cookieName))
        cookie = self.cursor.fetchone()
        if (cookie):
            return Cookie(cookie[1], cookie[2], cookie[3], cookie[5], cookie[4], cookie[0])
        return None
    
    def insertCookie(self, cookie:Cookie)->None:

        self.cursor.execute(
            "INSERT INTO Cookies(cookieId, userId, cookieName, cookieValue, created, expired) values(?, ?, ?, ?, ?, ?)",
            (
                cookie.id,
                cookie.userId,
                cookie.name,
                cookie.value, 
                cookie.created,
                cookie.expires
            )
        )
        self.database.commit()
    
    def destroyCookie(self):
        ...




