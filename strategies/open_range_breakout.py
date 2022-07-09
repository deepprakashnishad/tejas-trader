from kiteconnect import KiteTicker, KiteConnect
from utils import my_constants as mconst

access_token = "w9chul4eQmyV5wtz1kM4bcPTLlpnC2DI"

kws = KiteTicker(api_key=mconst.API_KEY, access_token=access_token)
kite = KiteConnect(api_key=mconst.API_KEY, access_token=access_token)

inst_token_list = [3771393, 7458561]


def on_ticks(ws, ticks):
    print(ticks)


def on_connect(ws, response):
    ws.subscribe(inst_token_list)

    ws.set_mode(ws.MODE_FULL, inst_token_list)


kws.on_ticks = on_ticks
kws.on_connect = on_connect

kws.connect()
