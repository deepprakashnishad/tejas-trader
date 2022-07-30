from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int

from base_document import BaseDocument
from database import Database, ObjectId

class ScreenerSchema(Schema):
    name = Str()
    description = Str()
    entry_conditions = Raw()
    timeframe = Int()
    compression = Int()
    transaction_type = Str(validate=validate.OneOf(["BUY", "SELL"]))

class Screener(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "Screener",
        "schema": ScreenerSchema,
    }