# coding: utf-8
"""
 @Topic:

 @Date: 2021/1/29

 @Author: other.z

 @Copyright（C）: 2020-2023 other.z Inc.   All rights reserved.

"""

import json
import ply.lex


class LexerError(Exception):
    pass


class Lexer:

    def tokenize(self, string, debug=False):
        """
        Maps a string to an iterator over tokens. In other words: [char] -> [token]
        :param string:
        :param debug:
        :return:
        """

        new_lexer = ply.lex.lex(module=self, debug=debug)
        new_lexer.latest_newline = 0
        new_lexer.string_value = None
        new_lexer.input(string)

        while True:
            t = new_lexer.token()
            if t is None: break
            t.col = t.lexpos - new_lexer.latest_newline
            yield t

        if new_lexer.string_value is not None:
            raise LexerError('Unexpected EOF in string literal or identifier')

    literals = '#@$&{.[](=,)}'

    reserved_words = {'V': 'VARIABLE', 'P': 'PARAMETER'}

    tokens = [
                 'ID',
                 'NUMBER',
                 'STRING'
             ] + list(reserved_words.values())

    t_ignore = ' \t'

    def t_ID(self, t):
        r"""[a-zA-Z_][a-zA-Z0-9_]*"""
        t.type = self.reserved_words.get(t.value, 'ID')
        return t

    def t_NUMBER(self, t):
        r"""-?\d+"""
        t.value = int(t.value)
        return t

    def t_STRING(self, t):
        r"""\"([^\\\n]|(\\.))*?\""""
        t.value = json.loads(t.value)
        return t

    # Counting lines, handling errors
    def t_newline(self, t):
        r"""\n"""
        t.lexer.lineno += 1
        t.lexer.latest_newline = t.lexpos

    def t_error(self, t):
        raise LexerError('Error on line %s, col %s: Unexpected character: %s ' % (
            t.lexer.lineno, t.lexpos - t.lexer.latest_newline, t.value[0]))


if __name__ == '__main__':

    def main():

        data = '''22.035fads@!$$$'''
        # data = '"9fdsafd*.\ssd/${aaa}"'
        lexer = Lexer()
        for token in lexer.tokenize(data):
            print(token)

    main()