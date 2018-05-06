"""
常用功能函数
"""
import time

def log(*args, **kwargs):
    sep = '*' * 10
    print(sep, 'args :', *args, sep, **kwargs)

def datetime_to_timestamp(dtime):
    stamp = time.mktime(dtime.timetuple())
    return stamp
