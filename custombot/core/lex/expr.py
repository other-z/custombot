# coding: utf-8
"""
 @Topic:

 @Date: 2021/1/29

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import json
from typing import Dict, Any
from pydantic import BaseModel
from .functional import *


class ClexDatum(BaseModel):
    variable: Dict = {}
    parameter: Dict = {}
    context: Dict = {}
    retvalue: Any = None


class ClexFunctionNotFoundError(Exception):
    pass


class DatumInContext(object):

    @classmethod
    def wrap(cls, data):
        return isinstance(data, cls) and data or cls(data)

    def __init__(self, value, path=None, context=None):
        self.path = path
        self.value = value
        self.context = context

    @property
    def full_path(self):
        if self.context:
            if self.context.path is None:
                return self.path

            full_path = self.context.full_path
            if full_path == '~':
                return self.path
            return full_path
        return Root('~')

    def __repr__(self):
        return 'Datum(value=%r, path=%r, context=%r)' % (self.value, self.path, self.context)


class Expression:

    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    def find(self, data):
        raise NotImplementedError()

    def visit(self, data) -> DatumInContext:
        context = DatumInContext.wrap(data)
        datum = self.find(context)
        return datum

class Root(Expression):

    def find(self, datum) -> DatumInContext:
        if datum.context:
            return Root(self.expr).find(datum.context)
        return DatumInContext(datum.value, path=self)

    def __str__(self):
        return str(self.expr)

    def __eq__(self, other):
        return other == self.expr


class Index(Expression):

    def __str__(self):
        return f"[Index({self.expr})]"

    def find(self, datum):
        if len(datum.value) > self.expr:
            return DatumInContext(datum.value[self.expr], path=self, context=datum)
        raise IndexError(f'expr {datum.full_path} out of index: {self}, datum: {datum.value}')

class Child(Expression):

    def __init__(self, expr, child):
        super().__init__(expr)
        self.child = child

    def __str__(self):
        right = self.child
        if isinstance(right, Context):
            right = f'[{right}]'
        elif isinstance(right, Field):
            right = f".{right}"
        return f'{self.expr}{right}'

    def find(self, datum):
        return self.child.visit(self.expr.visit(datum))


class Field(Expression):

    def __str__(self):
        return f"Field({self.expr})"

    def find(self, datum):
        field = isinstance(self.expr, Expression) and self.expr.visit(datum).value or self.expr

        try:
            field_value = datum.value[field] # Do NOT use `val.get(field)` since that confuses None as a value and None due to `get`
        except (TypeError, KeyError, AttributeError):
            if hasattr(datum.value, field):
                field_value = getattr(datum.value, field)
            else:
                raise KeyError(f'expr {datum.full_path} has no field: {self}, datum: {datum.value}')

        return DatumInContext(value=field_value, path=Field(field), context=datum)

class Function(Root):

    def __init__(self, funcname, args, kwargs):
        super().__init__(funcname)
        self.args = args
        self.kwargs = kwargs

    def find(self, datum):
        datum = super().find(datum)
        tr = lambda value: value.visit(datum).value if isinstance(value, Expression) else value

        args = [tr(value) for value in self.args]
        kwargs = {name: tr(value) for name, value in self.kwargs.items()}

        for fclass in [Time, Random, SafeCmper, Builtin]:
            function = getattr(fclass(), self.expr, None)
            if function:
                break
        else:
            raise ClexFunctionNotFoundError(self.expr)

        value = function(*args, **kwargs)
        datum = DatumInContext(value, path=self, context=datum)
        return datum

    def __str__(self):
        tr = lambda value: isinstance(value, Context) and str(value) or json.dumps(value)
        parameters = [f"Arg({tr(value)})" for value in self.args] + \
                     [f"Kwarg({name}={tr(value)})" for name, value in self.kwargs.items()]
        parameters = ",".join(parameters)
        return f"${{Func[{self.expr}]({parameters})}}"

class Context(Root):
    iden = '$'
    scope = ''

    def find(self, datum):
        datum = super().find(datum)
        if not isinstance(datum.value, ClexDatum):
            raise TypeError(f'expr {self} got error type datum: {datum}, type({type(datum.value)})')

        value = getattr(datum.value, self.__class__.__name__.lower())

        data = DatumInContext(value, path=self, context=datum)
        return self.expr.visit(data)

    def __str__(self):
        expr = self.scope and f"{self.scope}({self.expr})" or self.expr
        return f"{self.iden}{{{expr}}}"

class Variable(Context):
    scope = 'V'

class Parameter(Context):
    scope = 'P'

class RetValue(Context):
    iden = '@'
