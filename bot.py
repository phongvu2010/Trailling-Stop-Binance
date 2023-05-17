from time import sleep

from binance import ThreadedWebsocketManager

btc_price = {'error': False}

def btc_trade_history(msg):
    ''' define how to process incoming WebSocket messages '''
    if msg['e'] != 'error':
        print(msg['c'])
        btc_price['last'] = msg['c']
        btc_price['bid'] = msg['b']
        btc_price['last'] = msg['a']
        btc_price['error'] = False
    else:
        btc_price['error'] = True

api_key = 'orxThbVS0OyqnMZ1shu51RxPYXWS1HCA5lxc8mDQ6AH1MOHHslpBjgYXSflxnDJX'
api_secret = '8YBdmg31G7Wcv8GOuyAykXSPrUzhq7XCDGTOUHc4rjEm8kJhVTmKf4XqbOb5wUtP'

# init and start the WebSocket
bsm = ThreadedWebsocketManager(api_key = api_key, api_secret = api_secret)
bsm.start()

# subscribe to a stream
bsm.start_symbol_ticker_socket(callback = btc_trade_history, symbol = 'BTCUSDT')

sleep(20)

# stop websocket
bsm.stop()