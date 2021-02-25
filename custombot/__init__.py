# coding: utf-8
"""
 @Topic:

 @Date: 2021/1/22

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

from .core.lex.scope import R, RET, C, CTX, F, V, VAR, P
from .core.template import CustomBot, step, dep

__all__ = ['CustomBot', 'step', 'dep', 'R', 'RET', 'C', 'CTX', 'F', 'V', 'VAR', 'P']
