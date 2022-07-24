from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int

from base_document import BaseDocument
from database import Database, ObjectId

class StrategySchema(Schema):
    _id = ObjectId()
    name = Str(required=True)
    description = Str()
    symbols = Raw()
    entry_conditions = Raw()
    exit_conditions = Raw()
    stoploss = Float()
    target = Float()
    max_bet = Float()
    quantity = Int()
    timeframe = Int()
    compression = Int()
    transaction_type = Str(validate=validate.OneOf(["BUY", "SELL"]))
    order_type = Str(validate=validate.OneOf(["MARKET", "LIMIT", "SL", "SL-M"]))
    product = Str(validate=validate.OneOf(["MIS", "CNC", "NRML"]))


class Strategy(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "Strategy",
        "schema": StrategySchema,
    }