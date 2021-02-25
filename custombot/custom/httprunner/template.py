# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/7

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import copy
from urllib.parse import urljoin
from typing import Text, Dict, List
from custombot.core import *


class HttpRequest(Step):
    dependancy = Dependancy("custombot.keywords.httpclient:HttpSession", name="session")

    def validate(self, validater, source_value, expected_value, message=""):
        return super().validate(validater, source_value, expected_value, message=message or R.details)

    def assert_status_code(self, expected_value: int):
        return self.assert_equal(R.status_code, expected_value)

    def run(self, **kwargs) -> "HttpRequest":
        self._method = "request"
        self._kwargs.update(kwargs)
        return self

    def get(self, url, **kwargs):
        return self.run(method="get", url=url, **kwargs)

    def post(self, url, **kwargs):
        return self.run(method="post", url=url, **kwargs)

    def head(self, url, **kwargs):
        return self.run(method="head", url=url, **kwargs)

    def options(self, url, **kwargs):
        return self.run(method="options", url=url, **kwargs)

    def put(self, url, **kwargs):
        return self.run(method="put", url=url, **kwargs)

    def delete(self, url, **kwargs):
        return self.run(method="delete", url=url, **kwargs)

    def patch(self, url, **kwargs):
        return self.run(method="patch", url=url, **kwargs)

    def upload(self, _s=None, _default=False, **uploads):
        return self.__set_kwargs('upload', _s or uploads, default=_default)

    def with_headers(self, _s=None, _default=False, **headers):
        return self.__set_kwargs('headers', _s or headers, default=_default)

    def with_cookies(self, _s=None, _default=False, **cookies):
        return self.__set_kwargs('cookies', _s or cookies, default=_default)

    def with_params(self, _s=None, _default=False, **params):
        return self.__set_kwargs('params', _s or params, default=_default)

    def with_data(self, _s=None, _default=False, **data):
        return self.__set_kwargs('data', _s or data, default=_default)

    def with_json(self, _s=None, _default=False, **json):
        return self.__set_kwargs('json', _s or json, default=_default)

    def set_timeout(self, timeout: float, _default=False, ):
        return self.__set_kwargs('timeout', timeout, default=_default)

    def set_verify(self, verify: bool, _default=False):
        return self.__set_kwargs('verify', verify, default=_default)

    def set_allow_redirects(self, allow_redirects: bool, _default=False):
        return self.__set_kwargs('allow_redirects', allow_redirects, default=_default)

    def __set_kwargs(self, name, value, default):
        if default:
            self._kwargs.setdefault(name, value)
        else:
            self._kwargs[name] = value
        return self

    def __getattr__(self, item):
        return self._kwargs.get(item, None)


class HttpRunner(CustomBot):
    level: Text = 'P0'
    tags: List[Text] = []

    # default value for HttpRequest
    base_url: Text = ""
    verify: bool = False
    allow_redirects: bool = True
    timeout: int = 120

    headers: Dict[Text, Text] = {}

    __ignored__ = ['base_url', 'veryfy', 'allow_redirects', 'timeout', 'headers']

    @classmethod
    def dict(cls):
        for step in cls.setup + cls.steps + cls.teardown:
            if isinstance(step, HttpRequest):
                if step.url and "://" not in step.url and cls.base_url:
                    url = urljoin(cls.base_url, step.url)
                    step.run(url=url)

                step.set_verify(cls.verify, _default=True)
                step.set_timeout(cls.timeout, _default=True)
                step.set_allow_redirects(cls.allow_redirects, _default=True)

                if cls.headers:
                    headers = copy.deepcopy(cls.headers)
                    if step.headers:
                        headers.update(step.headers)
                    step.with_headers(headers)

        info = super().dict()
        return info
