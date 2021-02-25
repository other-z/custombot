# coding: utf-8
"""
 @Topic:

 @Date: 2020/12/8

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import py
import os
import json
import yaml
import warnings
from dotenv import dotenv_values, find_dotenv


class _LoaderBase:
    suffixs = []

    def __init__(self, filepath):
        self.fspath = py.path.local(filepath)

    def load(self):
        raise NotImplementedError()

    @classmethod
    def loaded(cls, file):
        _, suffix = os.path.splitext(file)
        if not suffix:
            suffix = cls.suffixs[0]
            file = f"{file}{suffix}"

        if os.path.exists(file) and suffix in cls.suffixs:
            loader = cls(file)
            return loader.load() or {}
        return None

    def __str__(self):
        return self.__class__.__name__


class JsonFileLoader(_LoaderBase):
    suffixs = ['.json']

    def load(self):
        with self.fspath.open() as f:
            return json.loads(f.read())


class YamlFileLoader(_LoaderBase):
    suffixs = ['.yaml', '.yml']

    def load(self):
        with self.fspath.open() as f:
            return yaml.safe_load(f.read())


class PyFileLoader(_LoaderBase):
    suffixs = ['.py']

    def load(self):
        return self.fspath.pyimport()


class EnvFileLoader(_LoaderBase):
    suffixs = ['.env']

    def load(self):
        return dotenv_values(find_dotenv(str(self.fspath), raise_error_if_not_found=True))


class FileLoader:

    @classmethod
    def load(cls, file):
        for loader in [JsonFileLoader, YamlFileLoader, PyFileLoader, EnvFileLoader]:
            try:
                s = loader.loaded(file)
            except:
                warnings.warn(f"loader[{loader}] load file '{file}' error")
                raise

            if s is not None:
                return s
        else:
            raise FileNotFoundError(file)
