from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int, DateTime

from base_document import BaseDocument
from database import Database, ObjectId

class DerivativeAnalysisResultSchema(Schema):
    _id = ObjectId()
    delivery_change = Float()
    close = Float()
    high = Float()
    low = Float()
    open = Float()
    datetime = Raw()
    coi_change = Float(required=False,  allow_null=True, allow_nan=True)
    delivery = Float()
    avg_del = Float()
    vwap = Float()
    oi_combined = Float()
    price_change = Float()
    position = Str()
    stock = Str()
    net_ce_change = Float(required=False,  allow_null=True, allow_nan=True)
    net_pe_change = Float(required=False,  allow_null=True, allow_nan=True)
    pcr = Float(required=False,  allow_null=True, allow_nan=True)
    change_list = Raw(required=False,  allow_null=True, allow_nan=True)
    pivot_points = Raw(required=False,  allow_null=True, allow_nan=True)
    net_pe = Float(required=False,  allow_null=True, allow_nan=True)
    max_pain_pe = Raw(required=False,  allow_null=True, allow_nan=True)
    max_pain_ce = Raw(required=False,  allow_null=True, allow_nan=True)
    net_ce = Float(required=False,  allow_null=True, allow_nan=True)
    pcr_of_change = Float(required=False,  allow_null=True, allow_nan=True)
    net_ce_change_pct = Float(required=False,  allow_null=True, allow_nan=True)
    net_pe_change_pct = Float(required=False,  allow_null=True, allow_nan=True)
    priority = Int(required=False,  allow_null=True, allow_nan=True)

class DerivativeAnalysisResult(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "DerivativeAnalysisResult",
        "schema": DerivativeAnalysisResultSchema,
    }