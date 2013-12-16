'''
Created on Dec 15, 2013

@author: ari
'''
import decimal

def json_encode_decimal(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, str):
        return obj
    raise TypeError(repr(obj) + " is not JSON serializable")