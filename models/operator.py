from marshmallow import Schema
from marshmallow.fields import Str, Raw, Boolean

from base_document import BaseDocument
from database import Database, ObjectId

class OperatorSchema(Schema):
    _id = ObjectId()
    name = Str(required=True)
    description = Str()
    tech_args = Raw()
    is_unary = Boolean()

class Operator(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "Operator",
        "schema": OperatorSchema,
    }