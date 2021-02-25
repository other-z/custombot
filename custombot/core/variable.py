# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/4

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""


from collections import OrderedDict


class Variable(OrderedDict):

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        if not key.startswith('_OrderedDict__'):
            self[key] = value
        else:
            OrderedDict.__setattr__(self, key, value)

    def __delattr__(self, key):
        try:
            self.pop(key)
        except KeyError:
            OrderedDict.__delattr__(self, key)

    def __eq__(self, other):
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return '{%s}' % ', '.join('%r: %r' % (key, self[key]) for key in self)

    # Must use original dict.__repr__ to allow customising PrettyPrinter.
    __repr__ = dict.__repr__
