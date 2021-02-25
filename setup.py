# coding: utf-8
"""
 @Topic:

 @Date: 2021/1/25

 @Author: otherz

 @Copyright（C）: 2020-2023 otherz Inc.   All rights reserved.

"""

import re
import sys
import datetime
from setuptools import setup, find_packages

setup(
    install_requires=[
        'python-dotenv',
        'pydantic',
        'loguru',
        'pytest',
        'PyYAML'
    ],
)