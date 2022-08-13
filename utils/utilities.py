import math
import sys
from models.technical import Technical
from models.strategy import Strategy
from models.instrument import Instrument
from models.operator import Operator

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

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__