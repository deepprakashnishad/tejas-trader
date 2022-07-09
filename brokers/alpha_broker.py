import time
import os
from datetime import datetime
import logging
import kiteconnect
from dateutil.tz import tzoffset
import csv
from brokers.broker import Broker
from core.tejas import Tejas
from feeds.feed import Feed
from utils import my_constants as mconst
from model import *
from pandas import json_normalize


class AlphaBroker(Broker):
    symbol_token_dict = {}

    def __init__(self, apikey=mconst.ALPHA_KEY, instrument_tokens=[], exchange="NSE"):
        super(AlphaBroker, self).__init__(brokername="AlphaVantage", exchange=exchange)

        self.instrument_tokens = instrument_tokens
        self.apikey = apikey

    def place_order(self, symbol_id, transaction_type, qty, **kwargs):
        self.orders.append(
            {
                "timestamp": datetime.now(),
                "symbol": symbol_id,
                "transaction_type": transaction_type,
                "price": kwargs['price'],
                "qty": qty,
                "order_type": kwargs['order_type'],
                "status": "OPEN"
            }
        )
        index = len(self.orders) - 1
        return self.execute_order(index, self.orders[index])

    def check_order_position_holding_exists(self, symbol, qty=1, types=None):
        if types is None:
            types = ["POSITIONS", "ORDERS"]
        total_qty = 0
        if "ORDERS" in types:
            for order in self.orders:
                if order['symbol'] == symbol and order['status'] == "OPEN":
                    total_qty = total_qty + order['qty']

        if "POSITIONS" in types:
            for position in self.positions:
                if position["symbol"] == symbol:
                    total_qty = total_qty + position['buy_qty'] - position['sell_qty']

        return total_qty

    def modify_order(self, index, **kwargs):
        self.orders[index] = [
            kwargs['symbol'],
            kwargs['bid_price'],
            kwargs['qty'],
            kwargs['order_type'],
            "PLACED"
        ]
        self.execute_order(self.orders)

    def cancel_order(self, index, **kwargs):
        self.orders[index, "status"] = "CANCELLED"

    def get_balance(self, **kwargs):
        return self.balance

    def get_user_detail(self, **kwargs):
        pass

    def get_positions(self):
        return self.positions

    def get_orders(self):
        return self.orders

    def get_historical_data(self, instrument_token, interval):
        url = mconst.ALPHA_URL + "&symbol=%s&interval=%s&outputsize=full&apikey=%s" % (
        instrument_token, interval, mconst.ALPHA_KEY)

    def get_live_data(self, **kwargs):
        pass

    def execute_order(self, index, order):
        i = -1
        self.orders[index]['status'] = "EXECUTED"
        for position in self.positions:
            i = i + 1
            if position['symbol'] == order['symbol']:
                if order['transaction_type'] == 'BUY':
                    new_qty = position['buy_qty'] + order['qty']
                    self.positions[i]['avg_buy_price'] = (position['buy_qty'] * position['avg_buy_price']
                                                          + order['qty'] * order['price']) / new_qty
                    self.positions[i]['buy_qty'] = new_qty

                elif order['transaction_type'] == 'SELL':
                    new_qty = position['sell_qty'] + order['qty']
                    self.positions[i]['avg_sell_price'] = (position['sell_qty'] * position[
                        'avg_sell_price'] + order['qty'] * order['price']) / new_qty
                    self.positions[i]['sell_qty'] = new_qty

                if self.positions[i]['sell_qty'] == self.positions[i]['buy_qty']:
                    new_profit = self.positions[i]['sell_qty'] * self.positions[i]['avg_sell_price'] \
                                 - self.positions[i]['buy_qty'] * self.positions[i]['avg_buy_price']
                    self.balance = self.balance + new_profit - self.commission
                    return new_profit - self.positions[i]['profit']
                else:
                    return

        if order['transaction_type'] == 'BUY':
            self.positions.append(
                {
                    'timestamp': datetime.now(),
                    'symbol': order['symbol'],
                    'position': order['transaction_type'],
                    'buy_qty': order['qty'],
                    'avg_buy_price': order['price'],
                    'sell_qty': 0,
                    'avg_sell_price': 0,
                    'profit': 0.0
                })
        else:
            self.positions.append(
                {
                    'timestamp': datetime.now(),
                    'symbol': order['symbol'],
                    'position': order['transaction_type'],
                    'sell_qty': order['qty'],
                    'avg_sell_price': order['price'],
                    'buy_qty': 0,
                    'avg_buy_price': 0,
                    'profit': 0.0
                })

    def set_tejas(self, tejas):
        self.tejas = tejas

    def set_tejas(self, tejas):
        self.tejas = tejas

    def set_feed(self, feed):
        self.feed = feed

    def udpate_trading_symbol_dict(self, instrument_tokens):
        # instrument_obj = Instrument.query.filter(Instrument.instrument_token != -1).
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
                'last_trade_time': datetime.datetime(2020, 3, 13, 15, 53, 8),
                'oi': 0, 'oi_day_high': 0, 'oi_day_low': 0,
                'timestamp': datetime.datetime(2020, 3, 13, 18, 20, 38),
            }
        ]
        min = 40
        max = 50
        last_ts = datetime.datetime.now()
        from random import random, randint
        while True:
            time.sleep(1)
            last_ts = last_ts + datetime.timedelta(seconds=1)
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
            print(f"Tick processed at {last_ts}")
