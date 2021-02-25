# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/2

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import inspect
from loguru import logger
from custombot import utils
from .lex.parser import CLexParser
from .validate import get_validater
from .session import CustomBotSession
from .model import CustomBot

clex_parser = CLexParser()


class CustomBotKWMethodNotFoundError(Exception):
    pass


class CustomBotRunner:

    def __init__(self, custombot, custombot_session):
        self.custombot_session: CustomBotSession = custombot_session
        self.custombot: CustomBot = custombot
        self.parameter = {}
        self.context = {}
        self.deps = {}

    def init(self):
        logger.debug(f"CUSTOMBOT[{self.custombot.name}]".center(100, "="))

        self.parameter = clex_parser.parse_source(
            self.custombot.parameter, variable=self.custombot_session.variables
        )
        logger.debug(f"[CUSTOMBOT]: parameter[P] => {self.parameter}")

    def extract(self, expr, allow_empty=False, **datum):
        if isinstance(expr, str):
            try:
                return clex_parser.parse_raw_string(expr, **datum)
            except (KeyError, IndexError):
                if allow_empty:
                    return None
                raise
        return expr

    def run_step(self, step):
        # check step condition is runable
        logger.debug(f"STEP[{step.name}]".center(100, "-"))
        logger.debug(f"[STEP]: {step}")

        if step.when is not True:
            condition = step.when
            condition = self.extract(condition, allow_empty=True, parameter=self.parameter,
                                     context=self.context, variable=self.custombot_session.variables)

            logger.debug(f"[STEP] WHEN[{step.when}]: {condition}({bool(condition)})")
            if not condition:
                logger.debug(f"[STEP] skiped!")
                return

        # create dep instance
        for dep in self.custombot.deps:
            if dep.name == step.dep:
                logger.debug(f'[STEP] {step.dep} = Dep({dep})')
                if dep.name in self.deps:
                    return self.deps[dep.name]

                instance, cls = utils.imports(dep.imports)
                if cls:
                    kwargs = clex_parser.parse_source(dep.kwargs, variable=self.custombot_session.variables)
                    instance = cls(**kwargs)

                custombot = getattr(instance, 'custombot', None)
                if custombot and inspect.isroutine(custombot):
                    custombot(self.custombot_session.metadatas)

                # dep is default to single_instance
                if dep.single_instance:
                    self.deps[dep.name] = instance

                break
        else:
            raise ValueError(f"unknown dep: {step.dep}")

        # run keyword method
        kwargs = clex_parser.parse_source(step.kwargs, context=self.context, parameter=self.parameter,
                                          variable=self.custombot_session.variables)
        logger.debug(f"[STEP] retvalue = {step.dep}.{step.method}(**{kwargs})")
        method = getattr(instance, step.method, None)
        if not method:
            raise CustomBotKWMethodNotFoundError(f"unknown keyword method '{step.method}'")

        i_args = kwargs.pop("ARGS", [])
        i_kwargs = kwargs.pop("KWARGS", {})
        retvalue = getattr(instance, step.method)(*i_args, **kwargs, **i_kwargs)
        logger.debug(f"[STEP] retvalue[R] => {retvalue}")

        # extract return values
        extracts = {
            name: self.extract(clex, allow_empty=True, retvalue=retvalue)
            for name, clex in step.extracts.items()
        }

        # update extracts to runner context
        if extracts:
            logger.debug(f"[STEP] extracts[C] <= {extracts}")

            # update extracts to runner context
            self.context.update(extracts)

        # validate the step's validates
        for validate in step.validates:
            # logger.debug(f"[STEP] Validater({validate})")
            source_value = self.extract(validate.source_value, retvalue=retvalue, context=self.context,
                                        parameter=self.parameter, variable=self.custombot_session.variables)

            expected_value = self.extract(validate.expected_value, retvalue=retvalue, context=self.context,
                                          parameter=self.parameter, variable=self.custombot_session.variables)

            message = self.extract(validate.message, retvalue=retvalue, context=self.context,
                                   parameter=self.parameter, variable=self.custombot_session.variables)

            # compare source_value and expected_value with validater
            log_message = f"[STEP] Validater({validate}) => <source_value[{repr(source_value)}]> {validate.cmper} " \
                      f"<expected_value[{repr(expected_value)}]> => "
            try:
                get_validater(validate.cmper).validate(source_value, expected_value, message)
                logger.debug(log_message + "PASS")
            except:
                logger.error(log_message + "FAIL")
                raise

    def run_steps(self, steps):
        for step in steps:
            self.run_step(step)

    def run(self):
        self.init()

        try:
            self.run_steps(self.custombot.setup)
            self.run_steps(self.custombot.steps)
        finally:
            self.run_steps(self.custombot.teardown)
