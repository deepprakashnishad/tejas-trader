from marshmallow import Schema
from marshmallow.fields import Str, Raw, Boolean, Integer

from base_document import BaseDocument
from database import Database, ObjectId

class InstrumentSchema(Schema):
    _id = ObjectId()
    instrument_token = Integer()
    tradingsymbol = Str(required=True)
    lot_size = Integer()
    instrument_type = Str()
    segment = Str()
    exchange = Str()

class Instrument(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "Instrument",
        "schema": InstrumentSchema,
    }

    def getInstrumentBySymbols(tokens):
        return Instrument.getMany(**{"instrument_token": {"$in": tokens}})