# coding: utf-8
"""
 @Topic:

 @Date: 2021/1/29

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import ply.yacc
from .lexer import Lexer
from .expr import *


class CLexParserError(Exception):
    pass


class IteratorToTokenStream(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def token(self):
        try:
            return next(self.iterator)
        except StopIteration:
            return None


class CLexParser:

    def parse(self, string, start_symbol='clex', debug=False) -> Expression:
        token_iterator = Lexer().tokenize(string, debug=debug)
        parser = ply.yacc.yacc(
            module=self,
            debug=debug,
            write_tables=0,
            start=start_symbol
        )
        return parser.parse(lexer=IteratorToTokenStream(token_iterator))

    def parse_clex_poses(self, string):
        poses = []
        stack = []
        for m in re.compile(r"([\@\$]\{)|(\})").finditer(string):
            if m.group(1):
                stack.append(m.start())
            elif stack:
                start = stack.pop()
                if not stack:
                    poses.append((start, m.end()))
        return poses

    def parse_raw_string(self, string, datum=None, **kwargs):
        # find clex strings
        poses = self.parse_clex_poses(string)
        if not poses:
            # it's a normal string!
            return string

        length = 0
        datums = {}
        datum = datum or ClexDatum(**kwargs)
        # visit clex value use datum
        for start, end in poses:
            clex = string[start:end]
            if clex not in datums:
                expr = self.parse(clex)
                datums[clex] = expr.visit(datum)

            length += end - start

        # if concat string with value
        if len(poses) > 1 or length != len(string):
            for clex, datum in datums.items():
                string = string.replace(clex, str(datum.value))
            return string

        # clex full matched string!
        _, datum = datums.popitem()
        return datum.value

    def parse_source(self, source, datum=None, **kwargs):
        datum = datum or ClexDatum(**kwargs)

        if isinstance(source, dict):
            return {name: self.parse_source(value, datum) for name, value in source.items()}

        elif isinstance(source, list):
            return [self.parse_source(value, datum) for value in source]

        elif isinstance(source, str):
            return self.parse_raw_string(source, datum)

        return source

    tokens = Lexer.tokens
    precedence = [
        ('left', ','),
        ('left', '.')
    ]

    def p_clex_function(self, p):
        """clex : '$' '{' ID '(' parameters ')' '}'"""
        p[0] = Function(p[3], **p[5])

    def p_clex_return(self, p):
        """clex : '@' '{' jsonpath '}'"""
        p[0] = RetValue(p[3])

    def p_clex_return_all(self, p):
        """clex : '@' '{' '@' '}'"""
        p[0] = RetValue(Root('@'))

    def p_clex_context(self, p):
        """clex : '$' '{' jsonpath '}'"""
        p[0] = Context(p[3])

    def p_clex_variable(self, p):
        """clex : '$' '{' VARIABLE '(' jsonpath ')' '}'"""
        p[0] = Variable(p[5])

    def p_clex_parameter(self, p):
        """clex : '$' '{' PARAMETER '(' jsonpath ')' '}'"""
        p[0] = Parameter(p[5])

    def p_jsonpath_field(self, p):
        """jsonpath : field"""
        p[0] = p[1]

    def p_jsonpath_binop(self, p):
        """jsonpath : jsonpath '.' jsonpath"""
        p[0] = Child(p[1], p[3])

    # for usage: "${E(sss.sss[1][${P(sss)}])}"
    def p_jsonpath_child_clex_brackets(self, p):
        """jsonpath : jsonpath '[' clex ']'"""
        p[0] = Child(p[1], Field(p[3]))

    def p_jsonpath_child_field_brackets(self, p):
        """jsonpath : jsonpath '[' field ']'"""
        p[0] = Child(p[1], p[3])

    def p_jsonpath_child_idx_brackets(self, p):
        """jsonpath : jsonpath '[' idx ']'"""
        p[0] = Child(p[1], p[3])

    def p_jsonpath_field_brackets(self, p):
        """jsonpath : '[' field ']'"""
        p[0] = p[2]

    def p_jsonpath_idx_brackets(self, p):
        """jsonpath : '[' idx ']'"""
        p[0] = p[2]

    def p_parameters(self, p):
        """parameters : args ',' kwargs"""
        p[0] = dict(args=p[1], kwargs=p[3])

    def p_parameters_args(self, p):
        """parameters : args
                      | empty"""
        args = p[1] or []
        p[0] = dict(args=args, kwargs={})

    def p_parameters_kwargs(self, p):
        """parameters : kwargs"""
        p[0] = dict(args=[], kwargs=p[1])

    def p_field(self, p):
        """field : ID
                 | STRING"""
        p[0] = Field(p[1])

    def p_kwargs(self, p):
        """kwargs : kwargs ',' kwargs"""
        p[1].update(p[3])
        p[0] = p[1]

    def p_kwarg(self, p):
        """kwargs : ID '=' value"""
        p[0] = {p[1]: p[3]}

    def p_args(self, p):
        """args : args ',' args"""
        p[0] = p[1] + p[3]

    def p_arg(self, p):
        """args : value"""
        p[0] = [p[1]]

    def p_value(self, p):
        """value : NUMBER
                 | STRING
                 | float
                 | clex"""
        p[0] = p[1]

    def p_float(self, p):
        """float : NUMBER '.' NUMBER"""
        p[0] = float(f"{p[1]}.{p[3]}")

    def p_idx(self, p):
        """idx : NUMBER"""
        p[0] = Index(p[1])

    def p_empty(self, p):
        """empty :"""
        p[0] = None

    def p_error(self, t):
        if not t:
            raise CLexParserError('Parse error: empty string! ')
        raise CLexParserError('Parse error at %s:%s near token %s (%s)' % (t.lineno, t.col, t.value, t.type))


if __name__ == '__main__':
    def main():
        yacc = CLexParser()
        # print(yacc.parse('sss."4".xxx[4].ooo', start_symbol='jsonpath'))

        data = [1, "2"]
        data = {"a": 1, "b": [1, "2", {"c": "4"}]}
        datum = ClexDatum(context=data, retvalue={"s": "c"}, variable={"url": 1})
        # print(yacc.parse('@{[1]}'))
        # print(yacc.parse('@{(sss."4".xxx}'))
        # print(yacc.parse("${E(sss.sss[1][${P(sss)}])}"))
        # print(yacc.parse("${E(sss)}"))
        # print(yacc.parse("${str(${sss.sss},1,4.5,\"fds\",a=1,b=2.9,c=\"2\")}"))
        # print(yacc.parse("${str(${sss.sss},1,4.5,\"fds\",a=1,b=2.9,c=\"2\")}"))
        # print(yacc.parse('@{@}'))

        expr = yacc.parse("${eq(1, 2)}")
        print(expr)

        datum = expr.visit(datum)
        print(datum.value, type(datum.value))


    main()
