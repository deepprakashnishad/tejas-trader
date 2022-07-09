import json
from utils import my_constants as mconst
from flask_marshmallow import Marshmallow
from flask_mongoalchemy import MongoAlchemy
from mongoalchemy.fields.fields import StringField, NumberField, DateTimeField, BoolField, EnumField, AnythingField, \
    IntField, FloatField, ObjectIdField
import datetime
from itertools import groupby
from types import ModuleType
from flask.json import JSONEncoder
import mongoengine
from flask import Flask
from bson import json_util, ObjectId
from idna import unicode
from pymongo import MongoClient

ma = Marshmallow()

app = Flask(__name__)
env = mconst.ENV;

if env=="PROD":
    db_url = mconst.PROD_DB_URL
    db_name = mconst.PROD_DB_NAME
    app.config["MONGOALCHEMY_REPLICA_SET"] = mconst.PROD_REPLICA_SET
else:
    db_url = mconst.DB_URL
    db_name = mconst.DB_NAME
    
# db_url = mconst.DB_URL
app.config["MONGOALCHEMY_DATABASE"] = db_name
app.config["MONGOALCHEMY_CONNECTION_STRING"] = db_url

db = MongoAlchemy(app)
client = MongoClient(db_url)
pmdb = getattr(client, db_name)


class MongoEngineJSONEncoder(JSONEncoder):
    def default(self, obj):
        if obj is None:
            return obj
        if isinstance(obj, (db.Document)):
            out = dict(obj._fields)
            for k, v in out.items():
                if isinstance(v, ObjectIdField):
                    if k is "mongo_id":
                        out['_id'] = str(obj.__getattribute__(k))
                        del (out[k])
                    else:
                        # Unlikely that we'll hit this since ObjectId is always NULL key
                        out[k] = str(obj.__getattribute__(k))
                elif k is "_id":
                    continue
                else:
                    try:
                        out[k] = obj.__getattribute__(k)
                    except:
                        print(f"{k} field not found")
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

    @classmethod
    def json_to_object(cls, obj, jsondata):
        out = dict(obj._fields)
        for k, v in out.items():
            if not isinstance(v, ObjectIdField):
                try:
                    obj.__setattr__(k, jsondata[k])
                except Exception as ex:
                    print(f"{k} not found in json")
        return obj


# from pymongo_model import PymongoDocument, PyMongoConnectionSingleton

# pmc = PyMongoConnectionSingleton("localhost", 27017, "quantTrader")

class User(db.Document):
    user_id = StringField()
    user_name = StringField()
    user_shortname = StringField()
    email = StringField()
    user_type = StringField()
    broker = StringField()
    exchanges = AnythingField()
    products = AnythingField()
    access_token = StringField()
    public_token = StringField()
    login_time = DateTimeField()
    avatar_url = StringField()
    access_token_expiry = DateTimeField()


class UserFundMargin(db.Document):
    user_id = StringField()
    equity = AnythingField()
    commodity = AnythingField()


class Holdings(db.Document):
    user_id = StringField()
    tradingsymbol = StringField()
    exchange = StringField()
    isin = StringField()
    quantity = IntField()
    t1_quantity = IntField()
    average_price = FloatField()
    last_price = FloatField()
    pnl = FloatField()
    product = EnumField(StringField(), "CNC", "NRML", "MIS")
    collateral_quantity = IntField()
    collateral_type = StringField()


class Instrument(db.Document):
    instrument_token = IntField()
    tradingsymbol = StringField()
    lot_size = IntField()
    instrument_type = StringField()
    segment = StringField()
    exchange = StringField()

    def getInstrumentBySymbols(tokens):
        print(tokens)
        return pmdb["Instrument"].find({"instrument_token": {"$in": tokens}})



class Position(db.Document):
    user_id = StringField()
    tradingsymbol = StringField()
    exchange: StringField()
    instrument_token = StringField()
    product = EnumField(StringField(), "CNC", "NRML", "MIS")
    quantity = IntField()
    overnight_quantity = IntField()
    multiplier = IntField()

    average_price = FloatField()
    close_price = FloatField()
    last_price = FloatField()
    value = FloatField()
    pnl = FloatField()
    m2m = FloatField()
    unrealised = FloatField()
    realised = FloatField()

    buy_quantity = IntField()
    buy_price = FloatField()
    buy_value = FloatField()
    buy_m2m = FloatField()

    day_buy_quantity = IntField()
    day_buy_price = FloatField()
    day_buy_value = FloatField()

    day_sell_price = FloatField()
    day_sell_value = FloatField()

    sell_quantity = IntField()
    sell_price = FloatField()
    sell_value = FloatField()
    sell_m2m = FloatField()


class PaperTrade(db.Document):
    symbol = StringField()
    buyPrice = FloatField()
    sellPrice = FloatField()
    enteredAt = DateTimeField()
    exitedAt = DateTimeField()
    positionTaken = BoolField()
    won = EnumField(StringField(), "Won", "Loss")


# variety 	regular 	Regular order
#   	amo 	After Market Order
#   	bo 	Bracket Order ?
#   	co 	Cover Order ?
# order_type 	MARKET 	Market order
#   	LIMIT 	Limit order
#   	SL 	Stoploss order ?
#   	SL-M 	Stoploss-market order ?
# product 	CNC 	Cash & Carry for equity ?
#   	NRML 	Normal for futures and options ?
#   	MIS 	Margin Intraday Squareoff for futures and options ?
# validity 	DAY 	Regular order
#   	IOC 	Immediate or Cancel

class Order(db.Document):
    order_id = StringField()
    parent_order_id = StringField()  # Useful for bracket order
    exchange_order_id = StringField()
    placed_by = StringField()
    tradingsymbol = StringField()
    exchange = StringField()
    transaction_type = EnumField(StringField(), "BUY", "SELL")
    order_type = EnumField(StringField(), "MARKET", "SL", "SL-M", "LIMIT")
    quantity = IntField()
    product = EnumField(StringField(), "CNC", "NRML", "MIS")
    price = FloatField()
    trigger_price = FloatField()
    average_price = FloatField()
    disclosed_quantity = IntField()
    pending_quantity = IntField()
    filled_quantity = IntField()
    validity = EnumField(StringField(), "DAY", "IOC")
    tag = StringField()
    squareoff = FloatField()  # Price difference at which the order should be squared off and profit booked (eg:
    # Order price is 100. Profit target is 102. So squareoff = 2
    stoploss = FloatField()  # Stoploss difference at which the order should be squared off (eg: Order price is 100.
    # Stoploss target is 98. So stoploss = 2
    trailing_stoploss = FloatField()
    status = EnumField(StringField(), "COMPLETE", "REJECTED", "CANCELLED", "OPEN")
    instrument_token = StringField()
    order_timestamp = IntField()
    exchange_timestamp = IntField()
    exchange_update_timestamp = IntField()
    status_message = StringField()


class HistoricalData(db.Document):
    symbol_id = AnythingField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    volume = IntField()
    open_interest = IntField()
    timeframe = IntField()
    compression = IntField()
    candle_creation_time = DateTimeField()


class Strategy(db.Document):
    name = StringField()
    description = StringField()
    symbols = AnythingField()
    entry_conditions = AnythingField()
    exit_conditions = AnythingField()
    stoploss = FloatField()
    target = FloatField()
    transaction_type = EnumField(StringField(), "BUY", "SELL")
    order_type = EnumField(StringField(), "MARKET", "LIMIT", "SL", "SL-M")
    product = EnumField(StringField(), "MIS", "CNC", "NRML")
    timeframe = IntField()
    compression = IntField()
    quantity = IntField()
    max_bet = FloatField()


class Technical(db.Document):
    name = StringField()
    description = StringField()
    tech_args = AnythingField()


class Operator(db.Document):
    name = StringField()
    description = StringField()
    is_unary = BoolField()
    tech_args = AnythingField()


class DeployStrategy(db.Document):
    user_id = StringField()
    strategy_ids = AnythingField()


class DerivativeAnalysisResult(db.Document):
    delivery_change = FloatField()
    close = FloatField()
    high = FloatField()
    low = FloatField()
    open = FloatField()
    coi_change = FloatField()
    delivery = FloatField()
    avg_del = FloatField()
    vwap = FloatField()
    oi_combined = FloatField()
    price_change = FloatField()
    position = StringField()
    stock = StringField()


class Screener(db.Document):
    name = StringField()
    description = StringField()
    entry_conditions = AnythingField()
    timeframe = IntField()
    compression = IntField()
    transaction_type = EnumField(StringField(), "BUY", "SELL")