from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int

from base_document import BaseDocument
from database import Database, ObjectId

class DeployStrategySchema(Schema):
    user_id = Str()
    strategy_ids = Raw()

class DeployStrategy(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "DeployStrategy",
        "schema": DeployStrategySchema,
    }