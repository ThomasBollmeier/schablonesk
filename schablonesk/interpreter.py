from schablonesk.ast import *


class Interpreter(BaseVisitor):

    def __init__(self, environment):
        BaseVisitor.__init__(self)
        self._env = environment
        self._stack = []

    def eval(self, ast):
        self._stack = []
        ast.accept(self)
        return self._stack.pop()

    def exit_logical_rel(self, logical_rel):
        right = self._stack.pop()
        left = self._stack.pop()
        op = logical_rel.op.lexeme
        if op == "==":
            result = left == right
        elif op == "<>":
            result = left != right
        elif op == ">":
            result = left > right
        elif op == ">=":
            result = left >= right
        elif op == "<":
            result = left < right
        elif op == "<=":
            result = left <= right
        else:
            raise Exception(f"Line {logical_rel.op.line_num}: Unknown operator {op}")
        self._stack.append(result)

    def visit_negation(self, negation):
        negation.expr.accept(self)
        value = self._stack.pop()
        self._stack.append(not value)

    def visit_expr(self, expr):
        if isinstance(expr, Identifier):
            name = expr.get_name()
            value = self._env.get_value(name)
            if value is None:
                raise Exception(f"Line {expr.token.line_num}: Identifier {name} is not defined")
            self._stack.append(value)
        elif isinstance(expr, Bool):
            self._stack.append(expr.get_bool_value())
        elif isinstance(expr, Int):
            self._stack.append(expr.get_int_value())
        elif isinstance(expr, Real):
            self._stack.append(expr.get_real_value())
        elif isinstance(expr, String):
            self._stack.append(expr.get_str_value())
        else:
            raise Exception(f"Line {expr.token.line_num}: Unsupported expression {expr.token.lexeme}")


