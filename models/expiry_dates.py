from marshmallow import Schema, validate
from marshmallow.fields import DateTime, Raw

from base_document import BaseDocument
from database import Database, ObjectId

class ExpiryDatesSchema(Schema):
    _id = ObjectId()
    expiryDate = Raw()

class ExpiryDates(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "ExpiryDates",
        "schema": ExpiryDatesSchema,
    }