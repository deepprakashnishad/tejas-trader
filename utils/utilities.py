import math


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