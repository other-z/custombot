# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/3

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import pytest
from _pytest import python
from _pytest.fixtures import FuncFixtureInfo
from _pytest.python import ExceptionInfo
from pydantic import ValidationError
from custombot.core.runner import CustomBotRunner
from custombot.core.session import CustomBotSession
from custombot import utils
from .model import TestCase



class CustomBotModule(python.Module):

    def _getobj(self):
        try:
            custombot = utils.get_custombot_from_file(self.fspath)
            return TestCase(**custombot)
        except ValidationError:
            raise self.CollectError(ExceptionInfo.from_current().value)
        except Exception as e:
            raise self.CollectError(e)

    def collect(self):
        testcase = self._getobj()
        yield CustomBotTestClass.from_parent(parent=self, testcase=testcase)


class CustomBotTestClass(python.Class):
    def __init__(self, *args, testcase=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.testcase = testcase

    @classmethod
    def from_parent(cls, **kwargs):
        return cls._create(name='()', **kwargs)

    def _getobj(self):
        return CustomBotRunner

    def collect(self):
        for testcase in self.testcase.cases:
            yield CustomBotInstance.from_parent(self, name="()", testcase=testcase)


class CustomBotInstance(python.Instance):

    def __init__(self, *args, testcase=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.testcase = testcase

    def _getobj(self):
        return CustomBotRunner(self.testcase, self.session.config.custombot_session)

    def collect(self):
        yield CustomBotTestCase.from_parent(
            self, name=self.testcase.name, callobj=CustomBotRunner.run,
            fixtureinfo=FuncFixtureInfo((), (), [], {})
        )


class CustomBotTestCase(python.Function):

    def _getobj(self):
        return getattr(self.parent, 'obj').run

    def setup(self):
        if isinstance(self.parent, CustomBotInstance):
            self.obj = self._getobj()
        # setattr(self, 'funcargs', {"custombot_session": self.session.config.custombot_session})

    def getmodpath(self, stopatmodule=True, includemodule=False):
        return self.name


@pytest.hookimpl(tryfirst=True)
def pytest_collect_file(path, parent):
    if path.basename.startswith('_'):
        return None

    elif path.ext in [".py", ".json", ".yml", ".yaml"]:
        return CustomBotModule.from_parent(parent, fspath=path)


def pytest_addoption(parser):
    parser.addoption("--variablefile", nargs='+', help="variable file.")


def pytest_sessionstart(session):
    custombot_session = CustomBotSession()
    session.config.custombot_session = custombot_session

    variable_args = session.config.getoption("--variablefile")
    if variable_args:
        variable_file = variable_args.pop(0)
        variables = utils.get_variables_from_file(variable_file, *variable_args)
        custombot_session.set_variables(variables)
        custombot_session.set_metadata(CUSTOMBOT_VARIABLE_FILE=variable_file)

    log_level = session.config.getoption("--log_level", default="DEBUG").upper()
    custombot_session.set_metadata(CUSTOMBOT_LOG_LEVEL=log_level)
