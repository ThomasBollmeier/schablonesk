import os
from schablonesk.ast import *


class AstPrinter(BaseVisitor):

    def __init__(self):
        BaseVisitor.__init__(self)
        self._indent_level = 0
        self._indent_size = 2

    def print(self, ast):
        ast.accept(self)

    def visit_template(self, templ):
        for block in templ.blocks:
            block.accept(self)

    def visit_text(self, text):
        s = text.content.strip()[:20]
        self._writeln(f"[{s}...]")

    def visit_cond(self, cond_block):
        self._writeln("cond")
        self._indent()
        for (cond, block) in cond_block.branches:
            self._writeln("branch")
            self._indent()
            cond.accept(self)
            block.accept(self)
            self._dedent()
        self._dedent()
        self._writeln("endcond")

    def visit_for(self, for_block):
        self._writeln("for")
        self._indent()
        self._writeln(f"item\t{self._expr_to_str(for_block.item_ident)}")
        self._writeln(f"listexpr\t{self._expr_to_str(for_block.list_expr)}")
        if for_block.filter_cond:
            self._write("filter\t")
            for_block.filter_cond.accept(self)

        for block in for_block.blocks:
            block.accept(self)

        self._dedent()
        self._writeln("endfor")

    def visit_logical_bin(self, logical_bin):
        self._writeln(logical_bin.op.lexeme)
        self._indent()
        logical_bin.left.accept(self)
        logical_bin.right.accept(self)
        self._dedent()

    def visit_logical_rel(self, logical_rel):
        self._writeln(logical_rel.op.lexeme)
        self._indent()
        logical_rel.left.accept(self)
        logical_rel.right.accept(self)
        self._dedent()

    def visit_expr(self, expr):
        self._writeln(self._expr_to_str(expr))

    def visit_negation(self, negation):
        self._write("not ")
        negation.expr.accept(self)

    @staticmethod
    def _expr_to_str(expr):
        if isinstance(expr, Identifier):
            return f"identifier(\"{expr.token.lexeme}\")"
        elif isinstance(expr, QualifiedName):
            return str(expr)
        elif isinstance(expr, SimpleValue):
            return str(expr.get_value())
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
