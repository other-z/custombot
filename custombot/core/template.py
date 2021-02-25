# coding: utf-8
"""
 @Topic:

 @Date: 2021/1/25

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

from typing import Text, Optional, Mapping, List, Dict
from .validate import get_validater
from .lex.scope import Scope


class ClassTemplateBase:
    __ignored__ = []

    @classmethod
    def _deep(cls, data):
        if isinstance(data, Mapping):
            return {name: cls._deep(value) for name, value in data.items() if not name.startswith('_')}

        elif isinstance(data, list):
            return [cls._deep(value) for value in data]

        elif isinstance(data, ClassTemplateBase):
            return data.dict()

        elif isinstance(data, Scope):
            return str(data)

        return data

    @classmethod
    def dict(cls):
        return cls._deep({name: value for name, value in cls.__dict__.items() if name not in cls.__ignored__})


class InstanceTemplateBase(ClassTemplateBase):

    def dict(self):
        return self._deep({name[1:]: value for name, value in self.__dict__.items() if name.startswith('_')})


class Dependancy(InstanceTemplateBase):

    def __init__(self, imports: Text, name: Text, single_instance: bool = False):
        self._name = name
        self._imports = imports
        self._kwargs = {}
        self._single_instance = single_instance

    @property
    def name(self):
        return self._name

    def __call__(self, **kwargs):
        self._kwargs = kwargs
        return self

    def __eq__(self, other):
        return isinstance(other, Dependancy) and other.name == self.name


class Step(InstanceTemplateBase):
    dependancy: Optional[Dependancy] = None

    def __init__(self, name: Text, dep: Text = None):
        self._dep = self.dependancy and self.dependancy.name or dep
        self._name = name
        self._method = None
        self._kwargs = {}
        self._validates = []
        self._extracts = {}
        self._when = True

    def run(self, method, **kwargs) -> "Step":
        """
        run the keyword method with kwargs
        eg: for dep("requests") you can request by:
        step("name", dep="s").run("post", url="https://birdframework.com")
        """
        if self._method:
            raise Exception(f"step[{self._name}] method '{self._method}' has registed!")
        self._method = method
        self._kwargs = kwargs
        return self

    def extract(self, **kwargs):
        """
        extract step's retvalue to context[C]
        :param kwargs:
        :return:
        """
        self._extracts.update(kwargs)
        return self

    def when(self, contidon: Scope):
        """
        set step runable condition
        eg: step("name", dep="s").when(C.status_code == 200)
        """
        self._when = contidon
        return self

    def validate(self, validater, source_value, expected_value, message=""):
        """
        validate the result of comparation  between source_value and expected_value
        such as: step("name", dep="s").validate("eq", 1, 1, "it's error message!")
        :return:
        """
        validater = get_validater(validater)
        self._validates.append(dict(
            cmper=validater.sim,
            source_value=source_value,
            expected_value=expected_value,
            message=message,
        ))
        return self

    def assert_equal(self, source_value, expected_value, message: Text = ""):
        """assert source_value == expected_value, message"""
        self.validate('equal', source_value=source_value, expected_value=expected_value, message=message)
        return self

    def assert_not_equal(self, source_value, expected_value, message: Text = ""):
        """assert source_value != expected_value, message"""
        self.validate('not_equal', source_value=source_value, expected_value=expected_value, message=message)
        return self

    def assert_greater_than(self, source_value, expected_value, message: Text = ""):
        """assert source_value > expected_value, message"""
        self.validate('greater_than', source_value=source_value, expected_value=expected_value, message=message)
        return self

    def assert_less_than(self, source_value, expected_value, message: Text = ""):
        """assert source_value < expected_value, message"""
        self.validate('less_than', source_value=source_value, expected_value=expected_value, message=message)
        return self

    def assert_greater_or_equals(self, source_value, expected_value, message: Text = ""):
        """assert source_value >= expected_value, message"""
        self.validate('greater_or_equals', source_value=source_value, expected_value=expected_value, message=message)
        return self

    def assert_less_or_equals(self, source_value, expected_value, message: Text = ""):
        """assert source_value <= expected_value, message"""
        self.validate('less_or_equals', source_value=source_value, expected_value=expected_value, message=message)
        return self

    def assert_regex_match(self, source_value, expected_value, message: Text = ""):
        """assert re.match(source_value, expected_value), message"""
        self.validate('regex_match', source_value=source_value, expected_value=expected_value, message=message)
        return self

    def assert_contained_by(self, source_value, expected_value, message: Text = ""):
        """assert source_value in expected_value, message"""
        self.validate('contained_by', source_value=source_value, expected_value=expected_value, message=message)
        return self

    def __getattr__(self, method):
        """the same to func:run"""
        return self.run(method)

    def __call__(self, **kwargs):
        """
        set keyword method's kwargs
        :param kwargs:
        :return:
        """
        if not self._method:
            raise UnboundLocalError(f'unknow method for step call! step name: {self._name}')

        self._kwargs = kwargs
        return self


class CustomBot(ClassTemplateBase):
    name: Text
    desc: Text = ''
    parameter: Dict = {}
    deps: List[Dependancy] = []
    setup: List[Step] = []
    steps: List[Step] = []
    teardown: List[Step] = []

    @classmethod
    def dict(cls):
        deps = list(cls.deps)
        for step in cls.setup + cls.steps + cls.teardown:
            if not step.dependancy:
                continue

            if step.dependancy not in deps:
                deps.append(step.dependancy)

        setattr(cls, 'deps', deps)
        return super().dict()

step = Step
dep = Dependancy