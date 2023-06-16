from binance.streams import ThreadedWebsocketManager

symbol = 'BNBBTC'

twm = ThreadedWebsocketManager()
# Start is required to initialise its internal loop
twm.start()

def handle_socket_message(msg):
    print(f"Message type: { msg['e'] }")
    print(msg)

twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

# # Multiple sockets can be started
# twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

# # or a multiplex socket can be started like this
# # see Binance docs for stream names
# streams = ['bnbbtc@miniTicker', 'bnbbtc@bookTicker']
# twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)

twm.join()
