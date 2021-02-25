# coding: utf-8
"""
 @Topic:

 @Date: 2021/2/1

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

from custombot.core.lex.parser import CLexParser, ClexDatum

parser = CLexParser()
retvalue = {
    "0": "0",
    "a": 1,
    "args": [11, "2", {"b": 111, "v": "2", "d": [1111, 2222, 3333]}],
    "kwargs": {"e": 11111, "f": [111111, 222222], "g": {"h": "a"}}
}

clex_datum = ClexDatum(
    context=dict(name="context", **retvalue),
    env=dict(name="env", **retvalue),
    parameter=dict(name="parameter", **retvalue),
    retvalue=retvalue
)

def test_index():
    expr = parser.parse("[0]", start_symbol="jsonpath")
    datum = expr.visit([0, 1, 2, 3])
    assert datum.value == 0, 'expr: [0], value: [0, 1, 2, 3]'

    datum = expr.visit(retvalue)
    assert datum.value == 0, f'expr: [0], value: {retvalue}'

    try:
        expr.visit([])
    except IndexError:
        return

    assert False

def test_subscrib():
    expr = parser.parse('["0"]', start_symbol="jsonpath")
    datum = expr.visit(retvalue)
    assert datum.value == "0", f'expr: ["0"], value: {retvalue}'

def test_attr():
    expr = parser.parse("a", start_symbol="jsonpath")
    datum = expr.visit(retvalue)
    assert datum.value == 1, f'expr: a, value: {retvalue}'
