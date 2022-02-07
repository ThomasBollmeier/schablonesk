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
            blocks.append(self._block())

        return Template(blocks)

    def _block(self):
        if self._match(TEXT):
            return Text(self._consume())
        elif self._match(COND):
            return self._cond_block()
        elif self._match(FOR):
            return self._for_block()
        else:
            raise Exception("Expected Block")

    def _for_block(self):
        self._consume()
        item_ident = Identifier(self._consume(IDENTIFIER))
        self._consume(IN)
        list_expr = self._expr()
        blocks = []
        while not self._end_of_tokens():
            if self._match(ENDFOR):
                break
            blocks.append(self._block())
        self._consume(ENDFOR)
        return ForBlock(item_ident, list_expr, blocks)

    def _expr(self):
        return Identifier(self._consume(IDENTIFIER))  # TODO: reimplement

    def _cond_block(self):
        self._consume()
        branches = []
        while True:
            branches.append((self._condition(), self._block()))
            if self._match(ENDCOND):
                self._consume()
                break
        return CondBlock(branches)

    def _condition(self):
        if self._match(ELSE):
            self._consume()
            return TrueExpr()
        identifier_token = self._consume(IDENTIFIER)
        return Identifier(identifier_token)

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

