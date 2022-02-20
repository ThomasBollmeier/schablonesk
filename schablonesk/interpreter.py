from schablonesk.ast import *
from schablonesk.config import Config
from schablonesk.scanner import Scanner
from schablonesk.parser import Parser


class Interpreter(BaseVisitor):

    def __init__(self, environment):
        BaseVisitor.__init__(self)
        self._env = environment
        self._stack = []

    def eval(self, ast):
        if isinstance(ast, CondBlock):
            return self._eval_cond_block(ast)
        else:
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

    def exit_logical_bin(self, logical_bin):
        right = self._stack.pop()
        left = self._stack.pop()
        op = logical_bin.op.lexeme
        if op == "or":
            result = left or right
        elif op == "and":
            result = left and right
        else:
            raise Exception(f"Line {logical_bin.op.line_num}: Unknown operator {op}")
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

    def visit_text(self, text):
        config = Config.get()
        begin, end = config.get_templ_str_delimiters()
        cmd_line_begin = config.get_cmd_line_begin()
        content = text.content
        result = ""
        search_pos = 0
        while True:
            pos = content.find(begin, search_pos)
            if pos != -1:
                result += content[search_pos:pos]
                search_pos = pos + len(begin)
                pos = content.find(end, search_pos)
                if pos != -1:
                    expr_str = cmd_line_begin + content[search_pos:pos]
                    ast = Parser(Scanner().scan(expr_str)).parse_expr()
                    result += str(self.eval(ast))
                    search_pos = pos + len(end)
                else:
                    result += content[search_pos:]
                    break
            else:
                result += content[search_pos:]
                break
        self._stack.append(result)

    def _eval_cond_block(self, cond_block):
        for condition, block in cond_block.branches:
            if self.eval(condition):
                return self.eval(block)
        return ""





