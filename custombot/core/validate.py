# coding: utf-8
"""
 @Topic:

 @Date: 2020/7/16

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import inspect
from typing import Text
from .lex.functional import SafeCmper

error_message = """
ValidateError:
  - cmper: {cmper}[{sim}]
  - source_value: {source_value} ({source_value_type})
  - expected_value: {expected_value} ({expected_value_type}
  - message: {message}
"""


class ValidateBase:
    sim = None
    uniform = []

    def __init__(self):
        self.cmper = SafeCmper()

    def validate(self, source_value, expected_value, message=""):
        message = error_message.format(
            source_value=source_value, source_value_type=type(source_value),
            expected_value=expected_value, expected_value_type=type(expected_value),
            message=message, sim=self.sim, cmper=self.__class__.__name__
        )
        assert getattr(self.cmper, self.sim)(source_value, expected_value), message


class Equal(ValidateBase):
    sim = 'eq'
    uniform = ['equal', 'equals']


class NotEqual(ValidateBase):
    sim = 'ne'
    uniform = ['neq', 'not_equal', 'not_equals']


class GreaterThan(ValidateBase):
    sim = 'gt'
    uniform = ['greater_than']


class LessThan(ValidateBase):
    sim = 'lt'
    uniform = ['less_than']


class GreaterOrEquals(ValidateBase):
    sim = 'ge'
    uniform = ['gte', 'greater_or_equals']


class LessOrEquals(ValidateBase):
    sim = 'le'
    uniform = ['lte', 'less_or_equals']


class RegexMatch(ValidateBase):
    sim = 're'
    uniform = ['regex', 'regex_match']


class ContainedBy(ValidateBase):
    sim = 'inby'
    uniform = ['contained_by']


def get_validater(cmper: Text):
    for validater in globals().values():
        if inspect.isclass(validater) and issubclass(validater, ValidateBase) and (
                validater.sim == cmper or cmper in validater.uniform):
            return validater()
    raise TypeError(f'unknown validater: {cmper}')