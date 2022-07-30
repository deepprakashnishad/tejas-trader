from marshmallow import Schema, validate
from marshmallow.fields import Str, Raw, Boolean, Float, Int, DateTime

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
    public_token = Str()
    login_time = DateTime()
    avatar_url = Str()
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