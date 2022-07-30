from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int

from base_document import BaseDocument
from database import Database, ObjectId

class PaperTradeSchema(Schema):
    symbol = Str()
    buyPrice = Float()
    sellPrice = Float()
    enteredAt = DateTime()
    exitedAt = DateTime()
    positionTaken = Bool()
    won = Str(validate=validate.OneOf(["Won", "Loss"]))

class PaperTrade(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "PaperTrade",
        "schema": PaperTradeSchema,
    }