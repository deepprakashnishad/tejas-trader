from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int

from base_document import BaseDocument
from database import Database, ObjectId

class HoldingsSchema(Schema):
    user_id = Str()
    tradingsymbol = Str()
    exchange = Str()
    isin = Str()
    quantity = Int()
    t1_quantity = Int()
    average_price = Float()
    last_price = Float()
    pnl = Float()
    product = Str(validate=validate.OneOf(["CNC", "NRML", "MIS"]))
    collateral_quantity = Int()
    collateral_type = Str()

class Holdings(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "Holdings",
        "schema": HoldingsSchema,
    }