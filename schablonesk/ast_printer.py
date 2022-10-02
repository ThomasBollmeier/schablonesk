import os
from schablonesk.ast import *
from schablonesk.parser import IndentationUnit

class AstPrinter(BaseVisitor):

    def __init__(self):
        BaseVisitor.__init__(self)
        self._indent_level = 0
        self._indent_size = 2

    def print(self, ast):
        ast.accept(self)

    def visit_template(self, templ):
        for usage in templ.usages:
            usage.accept(self)
        for snippet in templ.snippets:
            snippet.accept(self)
        for block in templ.statements:
            block.accept(self)

    def visit_text(self, text):
        s = text.content.strip()[:20]
        self._writeln(f"[{s}...]")

    def visit_block(self, block):
        self._writeln("block")
        self._indent()
        for stmt in block.statements:
            stmt.accept(self)
        self._dedent()

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

        for block in for_block.statements:
            block.accept(self)

        self._dedent()
        self._writeln("endfor")

    def visit_assignment(self, assignment):
        self._writeln("assignment")
        self._indent()
        self._writeln(f"source: {self._expr_to_str(assignment.source)}")
        self._writeln(f"target: {assignment.target.lexeme}")
        self._dedent()

    def visit_snippet(self, snippet):
        self._writeln(f"snippet {snippet.name.lexeme}")
        self._indent()
        self._writeln("parameters: ")
        self._indent()
        for p in snippet.params:
            self._writeln(f"{p.lexeme} ")
        self._dedent()
        self._writeln()
        for block in snippet.statements:
            block.accept(self)
        self._dedent()
        self._writeln("endsnippet")

    def visit_snippet_call(self, snippet_call):
        self._writeln(f"pasted section from snippet {snippet_call.name.lexeme}")
        self._indent()
        self._writeln("arguments: ")
        self._indent()
        for arg in snippet_call.args:
            arg.accept(self)
        self._dedent()
        if snippet_call.indent:
            self._writeln("indentation: ")
            self._indent()
            value, unit = snippet_call.indent
            unit_str = "tabs" if unit == IndentationUnit.TABS else "spaces"
            self._writeln(f"value: {self._expr_to_str(value)}")
            self._writeln(f"unit: {unit_str}")
            self._dedent()
        self._writeln()
        self._dedent()

    def visit_call(self, func_call):
        self._writeln(f"call of function {func_call.callee.get_name()}")
        self._indent()
        self._writeln("arguments: ")
        self._indent()
        for arg in func_call.args:
            arg.accept(self)
        self._dedent()
        self._writeln()
        self._dedent()

    def visit_use(self, use):
        self._writeln(f"use template {use.template_name.get_string()}")
        self._indent()
        if use.names:
            for name, alias in use.names:
                if not alias:
                    self._writeln(f"import {name.lexeme}")
                else:
                    self._writeln(f"import {name.lexeme} as {alias.lexeme}")
        else:
            self._writeln("import everything")
        self._dedent()

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
            return expr.token.lexeme
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

    def _writeln(self, s=""):
        self._write(s + os.linesep)
