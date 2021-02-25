# coding: utf-8
"""
 @Topic:

 @Date: 2021/1/25

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import inspect
import importlib
from custombot.utils.loader import FileLoader
from custombot.core.template import CustomBot
from custombot.core.variable import Variable


def imports(module):
    module, _clsname = module, None
    if ':' in module:
        module, _clsname = module.rsplit(':', 1)

    _module, _class = importlib.import_module(module), None

    if _clsname:
        _class = getattr(_module, _clsname)
        if not inspect.isclass(_class):
            raise ImportError(f'{module} is not a valid class!')

    return _module, _class


def get_custombot_cls_from_module(module):
    for name, cls in module.__dict__.items():
        if inspect.isclass(cls) and issubclass(cls, CustomBot) and hasattr(cls, 'name'):
            return cls


def get_custombot_from_file(file):
    custombot = FileLoader.load(file)
    if not custombot:
        raise TypeError(f'{file} is not valid custombot file!')

    if inspect.ismodule(custombot):
        custombot = get_custombot_cls_from_module(custombot)
        if not custombot:
            raise TypeError(f'{file} is not valid custombot file!')
        custombot = custombot.dict()
    return custombot


def get_variables_from_file(fspath, *args):
    module = variables = FileLoader.load(fspath)
    if inspect.ismodule(module):
        func = getattr(module, 'get_variables', None)
        variables = func and func(*args) or {key: value for key, value in module.__dict__.items() if key.isupper()}
    return Variable(variables)
