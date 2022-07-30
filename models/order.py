from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int

from base_document import BaseDocument
from database import Database, ObjectId

class OrderSchema(Schema):
    order_id = Str()
    parent_order_id = Str()  # Useful for bracket order
    exchange_order_id = Str()
    placed_by = Str()
    tradingsymbol = Str()
    exchange = Str()
    transaction_type = Str(validate=validate.OneOf(["BUY", "SELL"]))
    order_type = Str(validate=validate.OneOf(["MARKET", "SL", "SL-M", "LIMIT"]))
    quantity = Int()
    product = Str(validate=validate.OneOf(["CNC", "NRML", "MIS"]))
    price = Float()
    trigger_price = Float()
    average_price = Float()
    disclosed_quantity = Int()
    pending_quantity = Int()
    filled_quantity = Int()
    validity = Str(validate=validate.OneOf(["DAY", "IOC"]))
    tag = Str()
    squareoff = Float()  # Price difference at which the order should be squared off and profit booked (eg:
    # Order price is 100. Profit target is 102. So squareoff = 2
    stoploss = Float()  # Stoploss difference at which the order should be squared off (eg: Order price is 100.
    # Stoploss target is 98. So stoploss = 2
    trailing_stoploss = Float()
    status = Str(validate=validate.OneOf(["COMPLETE", "REJECTED", "CANCELLED", "OPEN"]))
    instrument_token = Str()
    order_timestamp = Int()
    exchange_timestamp = Int()
    exchange_update_timestamp = Int()
    status_message = Str()

class Order(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "Order",
        "schema": OrderSchema,
    }