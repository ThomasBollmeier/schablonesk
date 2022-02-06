import os
from schablonesk.ast import *


class AstPrinter(BaseVisitor):

    def __init__(self):
        BaseVisitor.__init__(self)
        self._indent_level = 0
        self._indent_size = 2

    def print(self, ast):
        ast.accept(self)

    def visit_text(self, text):
        self._writeln("[...some text...]")

    def enter_cond(self, cond_block):
        self._writeln("cond")
        self._indent()

    def exit_cond(self, cond_block):
        self._dedent()
        self._writeln("endcond")

    def enter_cond_branch(self, if_block):
        self._writeln("branch:")
        self._indent()

    def exit_cond_branch(self, if_block):
        self._dedent()

    def visit_expr(self, expr):
        if isinstance(expr, Identifier):
            self._writeln(f"IDENT: {expr.ident_tok.lexeme}")
        elif isinstance(expr, TrueExpr):
            self._writeln("true")
        else:
            self._writeln("some expression")

    def _indent(self):
        self._indent_level += self._indent_size

    def _dedent(self):
        self._indent_level -= self._indent_size

    def _write(self, s):
        for _ in range(self._indent_level):
            s = " " + s
        print(s, end="")

    def _writeln(self, s):
        self._write(s + os.linesep)
