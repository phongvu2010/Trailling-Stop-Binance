from sqlalchemy import Column, DateTime, String, Float
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Kline(Base):
    __tablename__ = 'klines'

    start_time = Column(DateTime(), primary_key = True)
    symbol = Column(String(20), primary_key = True)
    open = Column(Float())
    high = Column(Float())
    low = Column(Float())
    close = Column(Float())
    volume = Column(Float())

    def __int__(self, start_time, symbol, open, high, low, close, volume):
        self.start_time = start_time
        self.symbol = symbol
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

class Order(Base):
    __tablename__ = 'orders'

    symbol = Column(String(20), primary_key = True)
    time_order = Column(DateTime())
    type = Column(String(10))
    act_price = Column(Float())
    limit_price = Column(Float())
    delta = Column(Float())

    def __int__(self, symbol, time_order, type, act_price, limit_price, delta):
        self.symbol = symbol
        self.time_order = time_order
        self.type = type
        self.act_price = act_price
        self.limit_price = limit_price
        self.delta = delta
