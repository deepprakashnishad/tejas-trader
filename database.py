from utils import my_constants as mconst   
from pymongo import MongoClient

import bson
from marshmallow import ValidationError, fields, missing

def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
  
@singleton
class Database:
    db = None
    client = None
  
    def __init__(self):
        env = mconst.ENV;
        if env=="PROD":
            db_url = mconst.PROD_DB_URL
            db_name = mconst.PROD_DB_NAME
            replica_set = mconst.PROD_REPLICA_SET
        else:
            db_url = mconst.DB_URL
            db_name = mconst.DB_NAME
            replica_set = mconst.DEV_REPLICA_SET
            
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
    
    def get_db(self):
        return self.db

class ObjectId(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return str(bson.ObjectId(value))
        except Exception:
            raise ValidationError("invalid ObjectId `%s`" % value)

    def _serialize(self, value, attr, obj):
        if value is None:
            return missing
        return str(value)