from datetime import datetime
import model as md
from brokers.broker import Broker
import pandas as pd


class TestBroker(Broker):
    orders = []
    positions = []
    users_df = {}

    def __init__(self, brokername="Test Broker", balance=50000, commission=0.0, exchange="NSE"):
        super(TestBroker, self).__init__(brokername=brokername, balance=balance,
                                         commission=commission, exchange=exchange)

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

    def get_historical_data(self, **kwargs):
        result = list(md.pmdb['HistoricalData'].aggregate([
            {'$sort': {'datetime': 1}},
            {"$match": {"$and": [
                {"stock": kwargs['instrument_token']},
                {"datetime": {"$lte": kwargs['to_date'], "$gte": kwargs['from_date']}}
            ]}},
            {"$project":{
                "_id": 0,
                "date": "$datetime",
                "open": "$open",
                "high": "$high",
                "low": "$low",
                "close": "$close",
                "delivery": "$delivery",
                "stock": "$stock"
            }}
        ]))
        return result

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