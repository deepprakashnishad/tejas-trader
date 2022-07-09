from kiteconnect import KiteConnect
from utils import my_constants as mconst
from model import *

mconst.ACCESS_TOKEN = "UkMh82q53zSWF1hEa1FuJqS5oADOJSXu"

kite = KiteConnect(api_key=mconst.API_KEY, access_token=mconst.ACCESS_TOKEN)

instruments = kite.instruments(exchange="NSE")

for instrument in instruments:
    db_instrument = Instrument.query.filter(
        Instrument.instrument_token == instrument["instrument_token"]).first()
    if db_instrument is None:
        instrument = Instrument(
            instrument_token=instrument["instrument_token"],
            tradingsymbol=instrument["tradingsymbol"],
            lot_size=instrument["lot_size"],
            instrument_type=instrument["instrument_type"],
            exchange=instrument["exchange"],
            segment=instrument["segment"],
        )
        instrument.save()
        print("Instrument saved successfully")
