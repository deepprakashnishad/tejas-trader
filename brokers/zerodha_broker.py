import time
import os
from datetime import datetime, timedelta
import logging
import kiteconnect
from dateutil.tz import tzoffset
import csv
from brokers.broker import Broker
from core.tejas import Tejas
from feeds.feed import Feed
from utils import my_constants as mconst
from utils.utilities import dotdict, is_access_token_valid
from models.user import User
from pandas import json_normalize

kite = None
kws = None

data = [
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 38),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 42.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 39),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 40),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.9, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 41),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 18.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 42),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 43),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 44),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 14.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 45),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 46),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 35.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 47),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 48),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 49),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 50),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 51),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 52),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 53),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 54),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 38, 55),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 56),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 57),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 58),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 20.3, 'high': 31.7, 'low': 23.0, 'close': 32.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 20, 59),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 21.3, 'high': 41.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 1)
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 2),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 3),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 10.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 5),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 6),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 8),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 9),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 11),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 12),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 13),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 14),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 15),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 16),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 18),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 20),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 23),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 24),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 25),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 28),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 29),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 33),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 35),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 37),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 39),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 42),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 45),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 48),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 50),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 55),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 58),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 37.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 21, 59),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 35.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 22, 00),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 22, 15),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 22, 30),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 22, 45),
        }
    ],
    [
        {
            'tradable': True,
            'mode': 'full',
            'instrument_token': 4451329,
            'last_price': 30.95,
            'last_quantity': 50,
            'average_price': 29.12,
            'volume': 20770964,
            'buy_quantity': 18865,
            'sell_quantity': 0,
            'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
            'change': 2.1452145214521403,
            'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
            'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
            'timestamp': datetime(2020, 3, 13, 18, 23, 1),
        }
    ]
]


class ZerodhaBroker(Broker):
    symbol_token_dict = {}

    def __init__(self, uid, instrument_tokens=[], exchange="NSE"):
        super(ZerodhaBroker, self).__init__(brokername="Zerodha", exchange=exchange)
        try:
            self.kite = kiteconnect.KiteConnect(api_key=mconst.API_KEY)
            self.instrument_tokens = instrument_tokens
            user = User.get(**{"user_id":uid})
            user = dotdict(user)
            is_token_valid = is_access_token_valid(user.login_time)
            print(f"Is token valid - {is_token_valid}")
            if user is not None and is_token_valid:
                self.kite.set_access_token(user.access_token)
            else:
                return None

            self.kws = kiteconnect.KiteTicker(
                api_key=mconst.API_KEY, access_token=user.access_token,
                reconnect_max_tries=250, reconnect_max_delay=5, debug=False)
            # self.symbol_token_dict = {4451329: 'ADANIPOWER', 3050241: 'YESBANK', 3677697: 'IDEA'}
            self.e = None
        except:
            print("Exception occured")
            return None
        # self.udpate_trading_symbol_dict(instrument_tokens)

    def reinitiate_kite():
        self.kite.set_access_token(user.access_token)
        self.kws = kiteconnect.KiteTicker(
            api_key=mconst.API_KEY, access_token=user.access_token,
            reconnect_max_tries=250, reconnect_max_delay=5, debug=False)

    def check_order_position_holding_exists(self, instrument_token, qty=1, types=None):
        if types is None:
            types = ["ORDERS", "POSITIONS"]
        orders = self.get_orders()
        positions = self.get_positions()
        total_qty = 0
        if "ORDERS" in types:
            for order in orders:
                if order['instrument_token'] == instrument_token and order['status'] == "OPEN":
                    total_qty = order['quantity']
        if "POSITIONS" in types:
            for position in positions['net']:
                if position["instrument_token"] == instrument_token and position['quantity'] != 0:
                    total_qty = total_qty + position['quantity']

        return total_qty

    def place_order(self, symbol_id, transaction_type, qty, **kwargs):
        result = self.kite.place_order(
            tradingsymbol=self.get_trading_symbol(symbol_id),
            exchange=kwargs['exchange'],
            transaction_type=transaction_type,
            variety=kwargs['variety'],
            quantity=qty,
            product=kwargs['product'],
            order_type=kwargs['order_type']
        )
        return result

    def cancel_order(self, **kwargs):
        result = self.kite.cancel_order()
        print(result)

    def get_positions(self):
        positions = self.kite.positions()
        return positions

    def get_orders(self):
        return self.kite.orders()

    def get_balance(self, **kwargs):
        result = self.kite.margins()

    def get_user_detail(self, **kwargs):
        result = self.kite.profile()
        print(result)

    def get_historical_data(self, **kwargs):
        response = self.kite.historical_data(
            instrument_token=kwargs['instrument_token'],
            from_date=kwargs['from_date'].replace(tzinfo=None),
            to_date=kwargs['to_date'].replace(tzinfo=None),
            interval=kwargs['interval'],
            continuous=kwargs['continuous'],
            oi=kwargs['oi']
        )
        return response

    def set_tejas(self, tejas):
        self.tejas = tejas

    def set_feed(self, feed):
        self.feed = feed

    def connect(self, **kwargs):
        if not hasattr(self.kws, "ws") or not self.kws.is_connected():
            self.kws.on_ticks = self.on_ticks
            self.kws.on_connect = self.on_connect
            self.kws.on_close = self.on_close
            self.append_instrument_tokens(m_instrument_tokens=kwargs['symbol_ids'])
            self.kws.connect(threaded=kwargs['threaded'])

    def set_mode(self, mode, instrument_tokens):
        self.kws.ws.set_mode(mode=mode, instrument_tokens=instrument_tokens)

    def subscribe(self, instrument_tokens):
        # for token in instrument_tokens:
        #     if token in self.kws.subscribed_tokens:
        #         del instrument_tokens[index]
        self.kws.ws.subscribe(instrument_tokens)

    def on_ticks(self, ws, ticks):
        # Callback to receive ticks.
        print("Ticks recieved from zerodha live")
        logging.debug("Ticks: {}".format(ticks))
        self.feed.on_tick_recieved(ticks)

    def on_connect(self, ws, response):
        ws.subscribe(self.instrument_tokens)
        ws.set_mode(mode=kiteconnect.KiteTicker.MODE_FULL, instrument_tokens=self.instrument_tokens)

    def on_close(self, ws, code, reason):
        # On connection close stop the event loop.
        # Reconnection will not happen after executing `ws.stop()`
        logging.debug("Connection closed....")
        logging.debug(f"Code: {code}, Reason: {reason}")
        # ws.stop()

    def append_instrument_tokens(self, m_instrument_tokens):
        for token in m_instrument_tokens:
            if token in self.kws.subscribed_tokens:
                del token
            elif token not in self.instrument_tokens:
                self.instrument_tokens.append(token)

    def get_trading_symbol(self, token):
        if not self.symbol_token_dict[token]:
            self.udpate_trading_symbol_dict([token])
        return self.symbol_token_dict[token]

    def udpate_trading_symbol_dict(self, instrument_tokens):
        instrument_obj = self.kite.instruments(self.exchange)
        df = json_normalize(instrument_obj)
        for token in instrument_tokens:
            result = df.loc[df['instrument_token'] == token]
            self.symbol_token_dict[token] = result['tradingsymbol'][result.index[-1]]
        print(self.symbol_token_dict)

    def get_sample_ticks(self, e):
        cnt = 0
        for ticks in data:
            cnt = cnt + 1
            print(f"Tick {cnt}")
            time.sleep(0.1)
            self.feed.on_tick_recieved(ticks, e)

    def sample_tick_generator(self):
        data = [
            {
                'tradable': True,
                'mode': 'full',
                'instrument_token': 4451329,
                'last_price': 30.95,
                'last_quantity': 50,
                'average_price': 29.12,
                'volume': 20770964,
                'buy_quantity': 18865,
                'sell_quantity': 0,
                'ohlc': {'open': 27.3, 'high': 31.7, 'low': 23.0, 'close': 30.3},
                'change': 2.1452145214521403,
                'last_trade_time': datetime(2020, 3, 13, 15, 53, 8),
                'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
                'timestamp': datetime(2020, 3, 13, 18, 20, 38),
            }
        ]
        min = 40
        max = 50
        last_ts = datetime.now()
        from random import random, randint
        while True:
            time.sleep(1)
            last_ts = last_ts + timedelta(seconds=1)
            mopen = min + (random() * (max - min))
            high = max + (max - min) + (random() * (max - min))
            low = min - (max - min) + (random() * (max - min))
            close = min + (random() * (max - min))
            volume = randint(8834783, 9999999)
            data[0]['volume'] = volume
            data[0]['ohlc']['open'] = mopen
            data[0]['ohlc']['close'] = close
            data[0]['ohlc']['low'] = low
            data[0]['ohlc']['high'] = high
            data[0]['timestamp'] = last_ts
            self.feed.on_tick_recieved(data)
            print(f"Tick processed at {last_ts} from sample tick generator")
