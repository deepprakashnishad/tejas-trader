from marshmallow import Schema, validate
from marshmallow.fields import Str, String, Raw, Boolean, Float, Int, DateTime

from base_document import BaseDocument
from database import Database, ObjectId

class UserSchema(Schema):
    _id = ObjectId()
    user_id = Str()
    user_name = Str()
    user_shortname = Str()
    email = Str()
    user_type = Str()
    broker = Str()
    exchanges = Raw()
    products = Raw()
    access_token = Str()
    refresh_token = Str()
    api_key = Str()
    order_types = Raw()
    enctoken = Raw()
    meta = Raw()
    public_token = Str()
    login_time = Raw(required=False, default=None, missing='', allow_null=True)
    avatar_url = String(required=False, default=None, missing='', allow_null=True)
    access_token_expiry = DateTime()

class User(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "User",
        "schema": UserSchema,
    }

class UserFundMarginSchema(Schema):
    user_id = Str()
    equity = Raw()
    commodity = Raw()

class UserFundMargin(BaseDocument):
    db = Database().get_db()
    meta = {
        "collection": "UserFundMargin",
        "schema": UserFundMarginSchema,
    }