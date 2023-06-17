from binance.streams import ThreadedWebsocketManager
from datetime import datetime
from pprint import pprint
from threading import Lock
from base_sql import Session, create_table
from models import CryptoPrice

class Kline():
    def __init__(self, session, symbol, interval = '5m'):
        self.session = session
        self.symbol = symbol
        self.interval = interval

        # Socket manager using threads
        self.twm = ThreadedWebsocketManager()
        self.lock = Lock()

    def handle_message(self, candle):
        self.lock.acquire()

        if candle['x']:
            # Create price entries
            crypto = CryptoPrice(start_time = datetime.fromtimestamp(candle['t'] / 1000),
                                 symbol = candle['s'],
                                 open = candle['o'],
                                 high = candle['h'],
                                 low = candle['l'],
                                 close = candle['c'],
                                 volume = candle['v'])
            try:
                self.session.add(crypto)
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                print(e)
            finally:
                self.session.close()

        self.lock.release()

    def handle_socket_message(self, msg):
        if 'k' in msg:
            self.handle_message(msg['k'])
        pprint(msg['k'])

    def run(self):
        # Start is required to initialise its interal loop
        self.twm.start()

        self.twm.start_kline_socket(symbol = self.symbol, interval = self.interval, callback = self.handle_socket_message)

        # Join the threaded managers to the main thread
        self.twm.join()

# This functions creates the table if it does not exist
create_table()

# Create a new session
session = Session()

Kline(session, 'BNBBTC').run()


# {
#     'e': 'kline',
#     'E': 1686999646296,
#     's': 'BNBBTC',
#     'k': {
#         't': 1686999600000,
#         'T': 1686999659999,
#         's': 'BNBBTC',
#         'i': '1m',
#         'f': 223785814,
#         'L': 223785873,
#         'o': '0.00928400',
#         'c': '0.00927800',
#         'h': '0.00928500',
#         'l': '0.00927800',
#         'v': '60.79000000',
#         'n': 60,
#         'x': False,
#         'q': '0.56432172',
#         'V': '17.87400000',
#         'Q': '0.16593718',
#         'B': '0'
#     }
# }