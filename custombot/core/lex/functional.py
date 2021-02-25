# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/1

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import re
import time
import inspect


def _cmp(func):
    def __cmp(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return False
    return __cmp


class MetaClass(type):

    def __new__(mcs, name, bases, clsdict):
        s = type.__new__(mcs, name, bases, clsdict)
        makemeta = getattr(s, '__makemeta__')
        for attrs in [clsdict] + [base.__dict__ for base in bases]:
            for funcname, value in attrs.items():
                # 如果是实例函数
                if not funcname.startswith("_") and inspect.isroutine(value):
                    setattr(s, funcname, makemeta(value))
        return s


class Cmper:

    def eq(self, a, b):
        return a == b

    def ne(self, a, b):
        return a != b

    def lt(self, a, b):
        return a < b

    def gt(self, a, b):
        return a > b

    def le(self, a, b):
        return a <= b

    def ge(self, a, b):
        return a >= b

    def inby(self, e, l):
        return e in l

    def re(self, patten, s):
        return bool(re.match(patten, s))


class SafeCmper(Cmper, metaclass=MetaClass):
    __makemeta__ = _cmp


class Builtin:

    def int(self, s):
        return int(s)

    def str(self, s):
        return str(s)

    def float(self, s):
        return float(s)

    def len(self, s):
        return len(s)


class Random:
    pass


class Time:

    def timestamp_s(self):
        """秒级时间戳"""
        return int(time.time())

    def timestamp_ms(self):
        """毫秒级时间戳"""
        return int(time.time() * 1000)
