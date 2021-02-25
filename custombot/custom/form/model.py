# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/3

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

from pydantic import BaseModel
from typing import List, Text, Any, Dict
from custombot.core.model import JSONValue, CustomBot


class Option(BaseModel):
    comment: Text
    value: JSONValue


class Field(BaseModel):
    type: Text
    name: Text
    comment: Text
    default: Any = None
    placeholder: Text = ""
    required: bool = True
    multiple: bool = False
    options: List[Option] = []

    def get_value(self, value):
        if value is None:
            if self.required and self.default is None:
                raise ValueError(f'Field[{self.name}] value is required!')
            return self.default

        elif self.type == 'string':
            return str(value)

        elif self.type == 'number':
            try:
                if '.' in value:
                    return float(value)
                return int(value)
            except:
                raise ValueError(f"Field[{self.name}] value error: {value}(type({self.type}) )")

        if self.options:
            temp_val = value
            if not isinstance(temp_val, list):
                if self.multiple:
                    raise TypeError("multiple selector's value must be type of <list>.")
                temp_val = [temp_val]

            elif not self.multiple:
                raise TypeError(f"selector[{self.name}]'s is not multiple, but value is list: {value}")

            valid_values = [option.value for option in self.options]
            for v in temp_val:
                if not v in valid_values:
                    raise ValueError(f"selector[{self.name}]'s value: {repr(v)} is not in options.")

        return value


class CustomToolRunner(CustomBot):
    parameter: List[Field] = []

    def with_parameter(self, parameter: Dict=None):
        parameter = {field.name: field.get_value(parameter.get(field.name)) for field in self.parameter}
        return self.copy(update=dict(parameter=parameter))
