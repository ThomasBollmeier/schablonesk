from schablonesk.ast import *
from schablonesk.token_category import *

class Parser(object):

    def __init__(self, tokens):
        self._tokens = tokens
        self._next_idx = 0
        self._end_idx = len(self._tokens) - 1

    def parse(self):
        return self._template()

    def _template(self):
        blocks = []

        while not self._end_of_tokens():
            if self._match(TEXT):
                blocks.append(Text(self._consume()))
            else:
                self._consume()

        return Template(blocks)

    def _match(self, token_catg):
        return self._tokens[self._next_idx].category == token_catg

    def _consume(self, token_catg=None):
        if self._end_of_tokens():
            raise Exception("Unexpected end of input")
        if token_catg is not None:
            if not self._match(token_catg):
                raise Exception(f"Expected token category {token_catg}")
        ret = self._tokens[self._next_idx]
        self._next_idx += 1
        return ret

    def _end_of_tokens(self):
        return self._next_idx > self._end_idx
