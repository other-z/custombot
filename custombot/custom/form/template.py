# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/3

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

from typing import Text, List, Any
from custombot.core.template import InstanceTemplateBase
from custombot.core import *


class Field(InstanceTemplateBase):
    type = None

    def __init__(self, comment: Text, placeholder: Text = '', default: Any = None, required: bool = True):
        self._comment = comment
        self._placeholder = placeholder
        self._default = default
        self._required = required
        self._type = self.__class__.type

    def __str__(self):
        return f"{self.__class__.__name__}[{self._comment}]"


class Option(InstanceTemplateBase):
    type = 'option'

    def __init__(self, comment, value):
        self._value = value
        self._comment = comment


class String(Field):
    type = 'string'


class Number(Field):
    type = 'number'


class Selector(Field):
    type = 'selector'

    def __init__(self, comment: Text, options: List, placeholder: Text = '',
                 default: Any = None, multiple: bool = False, required: bool = True):
        super().__init__(comment=comment, default=default, required=required, placeholder=placeholder)
        self._options = options
        self._multiple = multiple


class RadioGroup(Selector):
    type = 'radio'

    def __init__(self, comment: Text, options: List, default: Any = None, required: bool = True):
        super().__init__(comment, options=options, default=default, required=required)


class CheckboxGroup(RadioGroup):
    type = 'checkbox'


class CustomTool(CustomBot):

    @classmethod
    def dict(cls):
        info = super().dict()
        parameter = []
        for name, field in info['parameter'].items():
            field['name'] = name
            parameter.append(field)

        info['parameter'] = parameter
        return info


