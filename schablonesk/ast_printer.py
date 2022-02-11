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
        s = text.token.lexeme.strip()[:20]
        self._writeln(f"[{s}...]")

    def enter_cond(self, cond_block):
        self._writeln("cond")
        self._indent()

    def exit_cond(self, cond_block):
        self._dedent()
        self._writeln("endcond")

    def enter_cond_branch(self, cond_block):
        self._writeln("branch")
        self._indent()

    def exit_cond_branch(self, cond_block):
        self._dedent()

    def enter_for(self, for_block):
        self._writeln("for")
        self._indent()
        self._writeln(f"item\t{self._expr_to_str(for_block.item_ident)}")
        self._writeln(f"listexpr\t{self._expr_to_str(for_block.list_expr)}")

    def exit_for(self, for_block):
        self._dedent()
        self._writeln("endfor")

    def enter_logical_bin(self, logical_bin):
        self._writeln(logical_bin.op.lexeme)
        self._indent()

    def exit_logical_bin(self, logical_bin):
        self._dedent()

    def enter_logical_rel(self, logical_rel):
        self._writeln(logical_rel.op.lexeme)
        self._indent()

    def exit_logical_rel(self, logical_rel):
        self._dedent()

    def visit_expr(self, expr):
        self._writeln(self._expr_to_str(expr))

    @staticmethod
    def _expr_to_str(expr):
        if isinstance(expr, Identifier):
            return f"identifier(\"{expr.ident_tok.lexeme}\")"
        elif isinstance(expr, TrueExpr):
            return "true"
        else:
            return "some expression"

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
