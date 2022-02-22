class Template(object):

    def __init__(self, blocks):
        self.blocks = blocks

    def accept(self, visitor):
        visitor.visit_template(self)


class Text(object):

    def __init__(self, text_token):
        self._token = text_token

    def get_token(self):
        return self._token

    token = property(get_token)

    def _get_content(self):
        return self._token.lexeme

    content = property(_get_content)

    def accept(self, visitor):
        visitor.visit_text(self)


class CondBlock(object):

    def __init__(self, branches):
        self.branches = branches

    def accept(self, visitor):
        visitor.visit_cond(self)


class ForBlock(object):

    def __init__(self, item_ident, list_expr, blocks, filter_cond=None):
        self.item_ident = item_ident
        self.list_expr = list_expr
        self.blocks = blocks
        self.filter_cond = filter_cond

    def accept(self, visitor):
        visitor.visit_for(self)


class SingleToken(object):

    def __init__(self, token):
        self.token = token

    def accept(self, visitor):
        visitor.visit_expr(self)


class Identifier(SingleToken):

    def __init__(self, identifier_token):
        SingleToken.__init__(self, identifier_token)

    def get_name(self):
        return self.token.lexeme


class SimpleValue(SingleToken):

    def __init__(self, token):
        SingleToken.__init__(self, token)

    def get_value(self):
        raise Exception("Not implemented")


class Bool(SimpleValue):

    def __init__(self, bool_token):
        SimpleValue.__init__(self, bool_token)

    def get_value(self):
        s = self.token.lexeme
        return s == "true" or s == "else"


class String(SimpleValue):

    def __init__(self, str_token):
        SimpleValue.__init__(self, str_token)

    def get_value(self):
        return self.token.lexeme[1:-1].replace("\\'", "'")


class Int(SimpleValue):

    def __init__(self, int_token):
        SimpleValue.__init__(self, int_token)

    def get_value(self):
        return int(self.token.lexeme)


class Real(SimpleValue):

    def __init__(self, real_token):
        SimpleValue.__init__(self, real_token)

    def get_value(self):
        return float(self.token.lexeme)


class QualifiedName(object):

    def __init__(self, identifier_tokens):
        self.identifier_tokens = identifier_tokens

    def accept(self, visitor):
        visitor.visit_expr(self)

    def __str__(self):
        return ".".join(list(map(lambda ident: ident.lexeme, self.identifier_tokens)))


class LogicalBinExpr(object):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def accept(self, visitor):
        visitor.visit_logical_bin(self)


class LogicalRelation(object):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def accept(self, visitor):
        visitor.visit_logical_rel(self)


class Negation(object):

    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        visitor.visit_negation(self)


class BaseVisitor(object):

    def __init__(self):
        pass

    def visit_template(self, templ):
        pass

    def visit_text(self, text):
        pass

    def visit_cond(self, cond_block):
        pass

    def visit_for(self, for_block):
        pass

    def visit_expr(self, expr):
        pass

    def visit_logical_bin(self, logical_bin):
        pass

    def visit_logical_rel(self, logical_rel):
        pass

    def visit_negation(self, negation):
        pass
