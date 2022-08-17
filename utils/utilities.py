import math
import sys
from models.technical import Technical
from models.strategy import Strategy
from models.instrument import Instrument
from models.operator import Operator
from datetime import datetime
from dateutil import tz

def dict_nan_cleaner(dict):
    for k, v in dict.items():
        try:
            if math.isnan(v):
                dict[k] = 0
        except:
            pass

    return dict

def fillna(value, default=0):
    if math.isnan(value):
        return default
    return value

def str_to_class(classname):
    return globals()[classname]

def is_access_token_valid(login_time):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Kolkata')
    utc = datetime.utcnow()
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)

    if central.date()==login_time.date() and login_time.hour>=6:
        return True
    else:
        return False

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
