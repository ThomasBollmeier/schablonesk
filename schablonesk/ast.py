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


class Identifier(object):

    def __init__(self, identifier_token):
        self.ident_tok = identifier_token

    def accept(self, visitor):
        visitor.visit_expr(self)


class TrueExpr(object):

    def accept(self, visitor):
        visitor.visit_expr(self)


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

    def exit_cond(self, if_block):
        pass

    def enter_cond_branch(self, if_block):
        pass

    def exit_cond_branch(self, if_block):
        pass

    def visit_expr(self, expr):
        pass
