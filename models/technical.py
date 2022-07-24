from marshmallow import Schema
from marshmallow.fields import Str, Raw

from base_document import BaseDocument
from database import Database, ObjectId

class TechnicalSchema(Schema):
    _id = ObjectId()
    name = Str(required=True)
    description = Str()
    tech_args = Raw()

class Technical(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "Technical",
        "schema": TechnicalSchema,
    }