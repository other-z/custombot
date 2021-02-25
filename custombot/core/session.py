# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/4

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import os
import sys
from pydantic import BaseModel
from typing import Text, Optional, Dict


class CustomBotMetadata(BaseModel):
    CUSTOMBOT_BASE_DIR: Text
    CUSTOMBOT_LOG_LEVEL: Text = 'DEBUG'
    CUSTOMBOT_VARIABLE_FILE: Optional[Text] = None


class CustomBotSession:

    def __init__(self):
        base_dir = os.getenv('CUSTOMBOT_ROOT_DIR', os.getcwd())
        if base_dir not in sys.path:
            sys.path.append(base_dir)

        self.variables = {}
        self.metadatas = CustomBotMetadata(CUSTOMBOT_BASE_DIR=base_dir)

    def set_metadata(self, **kwargs):
        self.metadatas = self.metadatas.copy(update=kwargs)

    def set_variables(self, variables: Dict):
        self.variables.update(variables)
