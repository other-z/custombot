# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/5

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import time
import json
import urllib3
import requests
from typing import Dict, Optional, Union, Mapping, Text
from requests import Request, Response
from requests.exceptions import RequestException
from pydantic import BaseModel

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def lower_dict_keys(source):
    if not source or not isinstance(source, Mapping):
        return source
    return {str(name).lower(): value for name, value in source.items()}


class NetworkFailure(Exception):
    pass


class Timer:

    def __init__(self):
        self.start_timestamp = 0
        self.finish_timestamp = 0

    def __enter__(self):
        self.start_timestamp = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish_timestamp = time.time()

    @property
    def elapsed_ms(self):
        return round((self.finish_timestamp - self.start_timestamp) * 1000, 2)

    @property
    def elapsed(self):
        return int(self.finish_timestamp - self.start_timestamp)


class SockAddress:

    def __init__(self, connection):
        self.connection = connection

    @property
    def client(self):
        try:
            return self.connection.sock.getsockname()
        except Exception as ex:
            raise NetworkFailure(f"failed to get client address info: {ex}")

    @property
    def service(self):
        try:
            return self.connection.sock.getpeername()
        except Exception as ex:
            raise NetworkFailure(f"failed to get client address info: {ex}")


class HttpRequestMeta(BaseModel):
    url: Text
    method: Text
    headers: Dict = {}
    cookies: Dict = {}
    body: Optional[Union[Dict, Text]] = {}


class HttpResponseMeta(BaseModel):
    status_code: int = 200
    elapsed_ms: float = 0.0
    encoding: Optional[Text] = None
    headers: Dict = {}
    cookies: Dict = {}
    body: Union[Dict, Text] = {}
    error: Optional[Text] = None


class HttpRequest:
    def __init__(self, request):
        self.request = request
        self.headers = dict(request.headers)

        lower_key_headers = lower_dict_keys(self.headers)
        self.content_type = lower_key_headers.get("content-type", "")
        self.content_size = int(lower_key_headers.get("content-length") or 0)
        self.cookies = getattr(request, '_cookies').get_dict()

        self.body = request.body
        if self.body is not None:
            try:
                self.body = json.loads(self.body)
            except json.JSONDecodeError:
                # str: a=1&b=2
                pass
            except UnicodeDecodeError:
                # bytes/bytearray: request body in protobuf
                pass
            except TypeError:
                # neither str nor bytes/bytearray, e.g. <MultipartEncoder>
                pass

            if self.content_type and "multipart/form-data" in self.content_type:
                # upload file type
                self.body = "upload file stream (OMITTED)"

    @property
    def method(self):
        return self.request.method

    @property
    def url(self):
        return self.request.url

    @property
    def metadata(self):
        return HttpRequestMeta(
            url=self.url,
            method=self.method,
            headers=self.headers,
            cookies=self.cookies,
            body=self.body
        )

    def __str__(self):
        return f"<HttpRequest [{self.method}({self.url})]>"


class HttpResponse:

    def __init__(self, response, response_time_ms):
        self.encoding = response.encoding
        # ISO-8859-1 为网页未找到正确定义的字符集时的默认编码，去掉后会自动使用 chardet 探测编码'
        if response.encoding and response.encoding.upper() == "ISO-8859-1":
            response.encoding = None

        self.address = SockAddress(response)
        self.request = HttpRequest(response.request)
        self.response_time_ms = response_time_ms

        self.response = response
        self.headers = dict(response.headers)

        lower_key_headers = lower_dict_keys(self.headers)
        self.content_type = lower_key_headers.get("content-type", "")
        self.content_size = int(lower_key_headers.get("content-length") or 0)

        self.cookies = response.cookies.get_dict()

        try:
            self.body = self.response.json()
        except ValueError:
            self.body = self.text

        try:
            response.raise_for_status()
        except RequestException as ex:
            self.error = str(ex)
        else:
            self.error = None

    @property
    def elapsed(self):
        return self.response.elapsed

    @property
    def elapsed_ms(self):
        return self.response.elapsed.microseconds / 1000.0

    @property
    def histories(self):
        return [HttpResponse(response, self.response_time_ms - self.elapsed_ms)
                for response in self.response.history] + [self]

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def text(self):
        return self.response.text

    @property
    def content(self):
        return self.response.content

    @property
    def metadata(self):
        return HttpResponseMeta(
            status_code=self.status_code,
            elapsed_ms=self.elapsed_ms,
            headers=self.headers,
            cookies=self.cookies,
            encoding=self.encoding,
            content_size=self.content_size,
            error=self.error,
            body=self.body
        )

    @property
    def details(self):
        details = "DETAILED REQUEST & RESPONSE\n"
        details += "========= request details =========\n"
        details += f"{self.request.metadata.json(indent=4, ensure_ascii=False)}\n\n"
        details += f"======== response details ========\n"
        details += f"{self.metadata.json(indent=4, ensure_ascii=False)}"
        return details

    def __str__(self):
        return f"<HttpResponse [{self.status_code}]>"


class ApiResponse(Response):
    def raise_for_status(self):
        if hasattr(self, "error") and self.error:
            raise self.error
        Response.raise_for_status(self)


class HttpSession(requests.Session):

    def request(self, method, url, name=None, stream=True, timeout=120, **kwargs) -> HttpResponse:
        with Timer() as timer:
            try:
                response = super().request(method, url, timeout=timeout, stream=True, **kwargs)
            except RequestException as ex:
                response = ApiResponse()
                response.error = ex
                response.status_code = 0  # with this status_code, content returns None
                response.request = Request(method, url, **kwargs).prepare()

        response = HttpResponse(response, timer.elapsed_ms)
        return response


if __name__ == '__main__':
    s = HttpSession()
    res = s.request('get', "htt1ps://www.baidu.com")

    print(res.request)
