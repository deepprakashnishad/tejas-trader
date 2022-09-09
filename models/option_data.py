from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int, DateTime

from base_document import BaseDocument
from database import Database, ObjectId

class OptionDataSchema(Schema):
    _id = ObjectId()
    datetime = Raw()
    max_pain_ce = Raw()
    max_pain_pe = Raw()
    net_ce = Int()
    net_pe = Int()
    pcr = Float()
    stock= Str()

class OptionData(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "OptionData",
        "schema": OptionDataSchema,
    }