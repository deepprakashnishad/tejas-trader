from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int, DateTime

from base_document import BaseDocument
from database import Database, ObjectId

class HistoricalDataSchema(Schema):
    symbol_id = Raw()
    open = Float()
    high = Float()
    low = Float()
    close = Float()
    volume = Int()
    open_interest = Int()
    timeframe = Int()
    compression = Int()
    candle_creation_time = DateTime()

class HistoricalData(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "HistoricalData",
        "schema": HistoricalDataSchema,
    }