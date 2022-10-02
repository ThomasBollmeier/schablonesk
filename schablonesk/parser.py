from schablonesk.ast import *
from schablonesk.token_category import *


class Parser(object):

    def __init__(self, tokens):
        self._tokens = tokens
        self._next_idx = 0
        self._end_idx = len(self._tokens) - 1

    def parse(self):
        ret = self._template()
        if not self._end_of_tokens():
            raise Exception("Unexpected end of parse")
        return ret

    def parse_expr(self):
        ret = self._expr()
        if not self._end_of_tokens():
            raise Exception("Unexpected end of parse")
        return ret

    def _template(self):
        usages = []
        snippets = []
        blocks = []

        while not self._end_of_tokens():
            if self._match(USE):
                usages.append(self._use())
            elif self._match(SNIPPET):
                snippets.append(self._snippet())
            else:
                blocks.append(self._block())

        return Template(usages, snippets, blocks)

    def _block(self):
        if self._match(TEXT):
            return Text(self._consume())
        elif self._match(COND):
            return self._cond_block()
        elif self._match(FOR):
            return self._for_block()
        elif self._match(PASTE):
            return self._paste()
        else:
            return self._assignment()

    def _assignment(self):
        if self._match(IDENTIFIER):
            target = self._consume(IDENTIFIER)
            self._consume(LARROW)
            source = self._expr()
        else:
            source = self._expr()
            self._consume(RARROW)
            target = self._consume(IDENTIFIER)
        return Assignment(source, target)

    def _use(self):
        self._consume()
        names = []
        while not self._end_of_tokens() and self._match(IDENTIFIER):
            name = self._consume()
            if self._match(LPAR):
                self._consume()
                alias = self._consume(IDENTIFIER)
                self._consume(RPAR)
            else:
                alias = None
            names.append((name, alias))
        if names:
            self._consume(FROM)
        template_name = String(self._consume(STRING))
        return Use(template_name, names)

    def _paste(self):
        self._consume()
        snippet_name = self._consume(IDENTIFIER)
        self._consume(LPAR)
        args = []
        while not self._end_of_tokens() and not self._match(RPAR):
            args.append(self._expr())
        self._consume(RPAR)

        indent = None
        if self._match(INDENT):
            self._consume(INDENT)
            self._consume(BY)
            value = self._expr()
            if self._match(TABS):
                unit = IndentationUnit.TABS
                self._consume(TABS)
            else:
                unit = IndentationUnit.SPACES
                self._consume(SPACES)
            indent = (value, unit)

        return SnippetCall(snippet_name, args, indent)

    def _snippet(self):
        self._consume()
        snippet_name = self._consume(IDENTIFIER)
        self._consume(LPAR)
        params = []
        while not self._end_of_tokens() and not self._match(RPAR):
            params.append(self._consume(IDENTIFIER))
        self._consume(RPAR)
        blocks = []
        while not self._end_of_tokens() and not self._match(ENDSNIPPET):
            blocks.append(self._block())
        self._consume(ENDSNIPPET)
        return Snippet(snippet_name, params, blocks)

    def _for_block(self):
        self._consume()
        item_ident = Identifier(self._consume(IDENTIFIER))
        self._consume(IN)
        list_expr = self._expr()
        if self._match(WHERE):
            self._consume()
            filter_cond = self._logical_expr()
        else:
            filter_cond = None
        blocks = []
        while not self._end_of_tokens():
            if self._match(ENDFOR):
                break
            blocks.append(self._block())
        self._consume(ENDFOR)
        return ForBlock(item_ident, list_expr, blocks, filter_cond)

    def _expr(self):
        return self._logical_expr()

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
            return Bool(self._consume())
        return self._logical_expr()

    def _logical_expr(self):
        return self._disjunction()

    def _disjunction(self):
        ret = self._conjunction()
        while self._match(OR):
            token_or = self._consume()
            right = self._conjunction()
            ret = LogicalBinExpr(token_or, ret, right)
        return ret

    def _conjunction(self):
        ret = self._logical_rel()
        while self._match(AND):
            token_and = self._consume()
            right = self._logical_rel()
            ret = LogicalBinExpr(token_and, ret, right)
        return ret

    def _logical_rel(self):
        ret = self._negation()
        while self._match(EQ, NE, GT, GE, LT, LE):
            op = self._consume()
            right = self._negation()
            ret = LogicalRelation(op, ret, right)
        return ret

    def _negation(self):
        if self._match(NOT):
            self._consume()
            return Negation(self._primary())
        else:
            return self._primary()

    def _primary(self):
        if self._match(LPAR):
            self._consume()
            logical_expr = self._logical_expr()
            self._consume(RPAR)
            return logical_expr
        elif self._match(STRING):
            return String(self._consume())
        elif self._match(INT):
            return Int(self._consume())
        elif self._match(REAL):
            return Real(self._consume())
        elif self._match(TRUE) or self._match(FALSE):
            return Bool(self._consume())
        else:
            return self._qualified_name()

    def _qualified_name(self):
        identifier_tokens = [self._consume(IDENTIFIER)]
        while self._match(DOT):
            self._consume()
            identifier_tokens.append(self._consume(IDENTIFIER))
        if len(identifier_tokens) == 1:
            name = Identifier(identifier_tokens[0])
        else:
            name = QualifiedName(identifier_tokens)
        if not self._match(LPAR):
            return name
        # function or method call
        self._consume(LPAR)
        args = []
        while not self._end_of_tokens() and not self._match(RPAR):
            args.append(self._expr())
        self._consume(RPAR)
        return Call(name, args)

    def _match(self, *token_categories):
        if self._end_of_tokens():
            return False
        for token_catg in token_categories:
            if self._tokens[self._next_idx].category == token_catg:
                return True
        return False

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


class IndentationUnit:
    TABS = 1
    SPACES = 2