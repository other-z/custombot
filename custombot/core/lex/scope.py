# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/1

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import json
import functools
from custombot.core.lex.functional import *


def __get_string(value):
    if isinstance(value, Scope):
        return str(value)
    elif isinstance(value, (int, float, str)):
        return json.dumps(value, ensure_ascii=False)
    raise TypeError(value)


def _collect(func):
    @functools.wraps(func)
    def __collect(_, *args, **kwargs):
        parameter = [__get_string(arg) for arg in args] + \
                    [f"{name}={__get_string(value)}" for name, value in kwargs.items()]
        parameter = ", ".join(parameter)
        return Function(parameter, func.__name__)

    return __collect


class When:

    def re(self, patten):
        return CMP.re(patten, self)

    def inby(self, other):
        return CMP.inby(self, other)

    def __eq__(self, other):
        return CMP.eq(self, other)

    def __ne__(self, other):
        return CMP.ne(self, other)

    def __lt__(self, other):
        return CMP.lt(self, other)

    def __gt__(self, other):
        return CMP.gt(self, other)

    def __ge__(self, other):
        return CMP.ge(self, other)

    def __le__(self, other):
        return CMP.le(self, other)


class Scope:
    _iden = '$'

    def __init__(self, string='', scope=''):
        self._string = string
        self._scope = scope

    def __str__(self):
        if not self._string:
            raise ValueError(f'unknown scope: {self.__class__.__name__}')

        string = self._scope and f"{self._scope}({self._string})" or self._string
        return f"{self._iden}{{{string}}}"

    def __repr__(self):
        return self.__str__()


class Context(Scope, When):

    def __getattr__(self, item) -> "Context":
        if not self._string or self._string == self._iden:
            return self.__class__(item)
        return self.__class__(f"{self._string}.{item}")

    def __getitem__(self, item) -> "Context":
        item = isinstance(item, Scope) and str(item) or json.dumps(item)

        string = (self._string and self._string != self._iden) and self._string or ''
        return self.__class__(f"{string}[{item}]")


class Parameter(Context):

    def __init__(self, string=''):
        super().__init__(string, scope="P")


class Variable(Context):

    def __init__(self, string=''):
        super().__init__(string, scope="V")


class RetValue(Context):
    _iden = '@'
    def __init__(self, string=''):
        super().__init__(string or self._iden)


class Function(Scope, When, Random, Time, Builtin, metaclass=MetaClass):
    __makemeta__ = _collect


class Cmp(Scope, Cmper, metaclass=MetaClass):
    __makemeta__ = _collect


CMP = Cmp()
F = Function()
R = RET = RetValue()
C = CTX = Context()
V = VAR = Variable()
P = PAR = Parameter()


# if __name__ == '__main__':
#     x = {"a": C.a.p[1].b["sss"], "b": F.str(R[7].a.p[1].b["sss"])}
#     print(F.str(1))
#     print(V.a.p[1].b["sss"].inby("fsdfdsfds"))
#     print(P.a.p[1].b["sss"])
#     print(R[7].a.p[1].b["sss"])
#     print(x)
#     print(V.a.p[1].b["sss"])
