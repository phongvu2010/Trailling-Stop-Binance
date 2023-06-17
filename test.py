from binance import ThreadedWebsocketManager

# socket manager using threads
twm = ThreadedWebsocketManager()
twm.start()

def handle_socket_message(msg):
    print(f"message type: {msg['e']}")
    print(msg)

twm.start_kline_socket(callback=handle_socket_message, symbol='BNBBTC')

# replace with a current options symbol
options_symbol = 'BTC-210430-36000-C'
# join the threaded managers to the main thread
twm.join()