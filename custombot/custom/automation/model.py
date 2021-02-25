# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/3

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import warnings
from typing import Text, Union, List
from pydantic import BaseModel, conlist
from custombot.core.model import CustomBot, Kwargs


# DDT Case model
class Case(BaseModel):
    idx: int
    name: Text
    parameter: Kwargs


# DDT TestCase model
class TestCase(CustomBot):
    parameter: Union[Kwargs, conlist(Case, min_items=1)] = {}

    @property
    def cases(self):
        idx = []
        if isinstance(self.parameter, list):
            for case in self.parameter:
                if case.idx in idx:
                    warnings.warn(f'There are duplicate idx custombot{self.name}')
                    continue

                idx.append(case.idx)
                yield self.copy(update=dict(
                    idx=case.idx,
                    name=f"{self.name}::{case.name}",
                    parameter=case.parameter
                ))
        else:
            yield self