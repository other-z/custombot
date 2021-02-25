# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/2

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

from typing import List, Text, Dict
from custombot.core.template import InstanceTemplateBase
from custombot.core import *


class Case(InstanceTemplateBase):

    def __init__(self, name: Text, parameter: Dict, idx: int):
        """
        DDT case for TestCase
        :param name:
        :param parameter:
        :param idx: unique id (it's for specifing the case action of update and create)
        """
        self._idx = idx
        self._name = name
        self._parameter = parameter


class TestCase(CustomBot):
    name: Text
    level: Text = 'P0'
    tags: List[Text] = []

    @classmethod
    def debug(cls, *args):
        from .command import main
        main(args)

