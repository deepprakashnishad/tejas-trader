from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int

from base_document import BaseDocument
from database import Database, ObjectId

class DerivativeAnalysisResultSchema(Schema):
    delivery_change = Float()
    close = Float()
    high = Float()
    low = Float()
    open = Float()
    coi_change = Float()
    delivery = Float()
    avg_del = Float()
    vwap = Float()
    oi_combined = Float()
    price_change = Float()
    position = Str()
    stock = Str()

class DerivativeAnalysisResult(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "DerivativeAnalysisResult",
        "schema": DerivativeAnalysisResultSchema,
    }