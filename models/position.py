from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int

from base_document import BaseDocument
from database import Database, ObjectId

class PositionSchema(Schema):
    user_id = Str()
    tradingsymbol = Str()
    exchange: Str()
    instrument_token = Str()
    product = Str(validate=validate.OneOf(["CNC", "NRML", "MIS"]))
    quantity = Int()
    overnight_quantity = Int()
    multiplier = Int()

    average_price = Float()
    close_price = Float()
    last_price = Float()
    value = Float()
    pnl = Float()
    m2m = Float()
    unrealised = Float()
    realised = Float()

    buy_quantity = Int()
    buy_price = Float()
    buy_value = Float()
    buy_m2m = Float()

    day_buy_quantity = Int()
    day_buy_price = Float()
    day_buy_value = Float()

    day_sell_price = Float()
    day_sell_value = Float()

    sell_quantity = Int()
    sell_price = Float()
    sell_value = Float()
    sell_m2m = Float()

class Position(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "Position",
        "schema": PositionSchema,
    }