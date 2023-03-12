from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int, DateTime

from base_document import BaseDocument
from database import Database, ObjectId

class IndexOptionDataSchema(Schema):
    _id = ObjectId()
    datetime = Raw()
    max_pain_ce = Raw()
    max_pain_pe = Raw()
    net_ce = Int()
    net_pe = Int()
    change_in_ce = Int()
    change_in_pe = Int()
    net_change = Int()
    pcr = Float()
    stock= Str()

class IndexOptionData(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "IndexOptionData",
        "schema": IndexOptionDataSchema,
    }