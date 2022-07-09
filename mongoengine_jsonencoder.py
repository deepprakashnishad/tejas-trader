import datetime
from itertools import groupby
from types import ModuleType

import mongoengine
from flask import Flask
from flask.json import JSONEncoder
from bson import json_util, ObjectId
from mongoengine.base import BaseDocument
from mongoengine.queryset.base import BaseQuerySet


def encode_model(obj, recursive=False):
    if obj is None:
        return obj
    if isinstance(obj, (db.Document)):
        out = dict(obj._fields)
        for k, v in out.items():
            if isinstance(v, ObjectIdField):
                if k == "mongo_id":
                    out['_id'] = str(obj.__getattribute__(k))
                    del (out[k])
                else:
                    # Unlikely that we'll hit this since ObjectId is always NULL key
                    out[k] = str(obj.__getattribute__(k))
            elif k == "_id":
                continue
            else:
                out[k] = obj.__getattribute__(k)
    elif isinstance(obj, (mongoengine.Document, mongoengine.EmbeddedDocument)):
        out = dict(obj._data)
        for k, v in out.items():
            if isinstance(v, ObjectId):
                if k is None:
                    out['_id'] = str(v)
                    del (out[k])
                else:
                    # Unlikely that we'll hit this since ObjectId is always NULL key
                    out[k] = str(v)
            else:
                out[k] = obj.encode_model(v)
    elif isinstance(obj, mongoengine.queryset.QuerySet):
        out = obj.encode_model(list(obj))
    elif isinstance(obj, ModuleType):
        out = None
    elif isinstance(obj, groupby):
        out = [(g, list(l)) for g, l in obj]
    elif isinstance(obj, (list)):
        out = [obj.encode_model(item) for item in obj]
    elif isinstance(obj, (dict)):
        out = dict([(k, obj.encode_model(v)) for (k, v) in obj.items()])
    elif isinstance(obj, datetime.datetime):
        out = str(obj)
    elif isinstance(obj, ObjectId):
        out = {'ObjectId': str(obj)}
    elif isinstance(obj, (str, unicode)):
        out = obj
    elif isinstance(obj, float):
        out = str(obj)
    else:
        raise TypeError("Could not JSON-encode type '%s': %s" % (type(obj), str(obj)))
    return out


class MongoEngineJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseDocument):
            return json_util._json_convert(obj.to_mongo())
        elif isinstance(obj, BaseQuerySet):
            return json_util._json_convert(obj.as_pymongo())
        return JSONEncoder.default(self, obj)

