# coding: utf-8
"""
 @Topic:

 @Date: 2021/1/25

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import json
from pydantic import BaseModel, conlist
from typing import Dict, List, Text, Optional, Union


class JSONValue:

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        json.dumps(value)
        return value


Kwargs = Dict[Text, Optional[JSONValue]]


class CustomBotValidater(BaseModel):
    cmper: Text
    source_value: JSONValue
    expected_value: Optional[JSONValue]
    message: Text = ''


class CustomBotDependancy(BaseModel):
    name: Text
    imports: Text
    kwargs: Kwargs = {}
    single_instance: bool = True


class CustomBotStep(BaseModel):
    dep: Text
    name: Text
    method: Text
    kwargs: Kwargs = {}
    when: Union[bool, Text]
    validates: List[CustomBotValidater] = []
    extracts: Dict[Text, Text] = {}


class CustomBot(BaseModel):
    idx: int = 0
    name: Text
    desc: Text = ''
    parameter: Kwargs = {}
    deps: conlist(CustomBotDependancy, min_items=1)
    setup: List[CustomBotStep] = []
    steps: conlist(CustomBotStep, min_items=1)
    teardown: List[CustomBotStep] = []

if __name__ == '__main__':
    d = CustomBotDependancy(name="aaa", imports="sss")
    d.kwargs['ss'] = 2
    print(d.kwargs)
    dd = CustomBotDependancy(name=d.name, imports="ssss")
    print(dd.kwargs)
