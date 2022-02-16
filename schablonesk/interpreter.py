from schablonesk.ast import *
from schablonesk.values import *


class Interpreter(BaseVisitor):

    def __init__(self, environment):
        BaseVisitor.__init__(self)
        self._env = environment
        self._stack = []

    def eval(self, ast):
        self._stack = []
        ast.accept(self)
        return self._stack.pop()

    def visit_expr(self, expr):
        if isinstance(expr, Identifier):
            name = expr.get_name()
            value = self._env.get_value(name)
            if value is None:
                raise Exception(f"Line {expr.token.line_num}: Identifier {name} is not defined")
            self._stack.append(value)
        elif isinstance(expr, Bool):
            self._stack.append(BoolValue(expr.get_bool_value()))
        else:
            raise Exception(f"Line {expr.token.line_num}: Unsupported expression {expr.token.lexeme}")


