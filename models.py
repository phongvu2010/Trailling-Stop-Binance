from base_sql import Base
from sqlalchemy import DateTime, Column, String, Float

class CryptoPrice(Base):
    __tablename__ = 'price_data'

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
