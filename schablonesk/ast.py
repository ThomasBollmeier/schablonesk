class Template(object):

    def __init__(self, blocks):
        self._blocks = blocks

    def accept(self, visitor):
        visitor.enter_template(self)
        for block in self._blocks:
            block.accept(visitor)
        visitor.exit_template(self)


class Text(object):

    def __init__(self, text_token):
        self._token = text_token

    def get_token(self):
        return self._token

    token = property(get_token)

    def accept(self, visitor):
        visitor.visit_text(self)


class CondBlock(object):

    def __init__(self, branches):
        self.branches = branches

    def accept(self, visitor):
        visitor.enter_cond(self)
        for condition, block in self.branches:
            visitor.enter_cond_branch(self)
            condition.accept(visitor)
            block.accept(visitor)
            visitor.exit_cond_branch(self)
        visitor.exit_cond(self)


class ForBlock(object):

    def __init__(self, item_ident, list_expr, blocks, filter_cond=None):
        self.item_ident = item_ident
        self.list_expr = list_expr
        self.blocks = blocks
        self.filter_cond = filter_cond

    def accept(self, visitor):
        visitor.enter_for(self)
        for block in self.blocks:
            block.accept(visitor)
        visitor.exit_for(self)


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


class Bool(SingleToken):

    def __init__(self, bool_token):
        SingleToken.__init__(self, bool_token)

    def get_bool_value(self):
        s = self.token.lexeme
        return s == "true" or s == "else"


class String(SingleToken):

    def __init__(self, str_token):
        SingleToken.__init__(self, str_token)

    def get_str_value(self):
        return self.token.lexeme[1:-1].replace("\\'", "'")


class Int(SingleToken):

    def __init__(self, int_token):
        SingleToken.__init__(self, int_token)

    def get_int_value(self):
        return int(self.token.lexeme)


class Real(SingleToken):

    def __init__(self, real_token):
        SingleToken.__init__(self, real_token)

    def get_real_value(self):
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
        visitor.enter_logical_bin(self)
        self.left.accept(visitor)
        self.right.accept(visitor)
        visitor.exit_logical_bin(self)


class LogicalRelation(object):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def accept(self, visitor):
        visitor.enter_logical_rel(self)
        self.left.accept(visitor)
        self.right.accept(visitor)
        visitor.exit_logical_rel(self)


class BaseVisitor(object):

    def __init__(self):
        pass

    def enter_template(self, templ):
        pass

    def exit_template(self, templ):
        pass

    def visit_text(self, text):
        pass

    def enter_cond(self, cond_block):
        pass

    def exit_cond(self, cond_block):
        pass

    def enter_cond_branch(self, cond_block):
        pass

    def exit_cond_branch(self, cond_block):
        pass

    def enter_for(self, for_block):
        pass

    def exit_for(self, for_block):
        pass

    def visit_expr(self, expr):
        pass

    def enter_logical_bin(self, logical_bin):
        pass

    def exit_logical_bin(self, logical_bin):
        pass

    def enter_logical_rel(self, logical_rel):
        pass

    def exit_logical_rel(self, logical_rel):
        pass
