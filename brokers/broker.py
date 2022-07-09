from feeds.feed import Feed
from technicals.technical import *


class Broker:
    feed: Feed

    def __init__(self, brokername="Test Broker", balance=50000, commission=0.0, exchange="NSE"):
        self.name = brokername
        self.commission = commission
        self.exchange = exchange
        self.balance = balance

    def check_order_position_holding_exists(self, instrument_token, qty=1, types=["ORDER", "POSITION"]):
        pass

    def place_order(self, symbol_id, transaction_type, qty, **kwargs):
        pass

    def cancel_order(self, **kwargs):
        pass

    def get_balance(self, **kwargs):
        pass

    def get_user_detail(self, **kwargs):
        pass

    def get_positions(self):
        pass

    def get_orders(self):
        pass

    def get_historical_data(self, **kwargs):
        pass

    def get_live_data(self, **kwargs):
        pass

    def set_broker(self, broker):
        self.broker = broker

    def set_feed(self, feed):
        self.feed = feed