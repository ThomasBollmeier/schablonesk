import os
from schablonesk.ast import *
from schablonesk.config import Config
from schablonesk.scanner import Scanner
from schablonesk.parser import Parser
from schablonesk.environment import Environment


class Interpreter(BaseVisitor):

    def __init__(self, environment):
        BaseVisitor.__init__(self)
        self._env = environment
        self._stack = []

    def eval(self, ast):
        self._stack.append(None)
        ast.accept(self)
        return self._stack.pop()

    def _set_ret_value(self, value):
        self._stack[-1] = value

    def visit_template(self, templ):
        ret = ""
        for block in templ.blocks:
            ret += self.eval(block)
        self._set_ret_value(ret)

    def visit_text(self, text):
        config = Config.get()
        begin, end = config.get_templ_str_delimiters()
        cmd_line_begin = config.get_cmd_line_begin()
        content = text.content
        ret = ""
        search_pos = 0
        while True:
            pos = content.find(begin, search_pos)
            if pos != -1:
                ret += content[search_pos:pos]
                search_pos = pos + len(begin)
                pos = content.find(end, search_pos)
                if pos != -1:
                    expr_str = cmd_line_begin + content[search_pos:pos]
                    ast = Parser(Scanner().scan(expr_str)).parse_expr()
                    ret += str(self.eval(ast))
                    search_pos = pos + len(end)
                else:
                    ret += content[search_pos:]
                    break
            else:
                ret += content[search_pos:]
                break
        self._set_ret_value(ret)

    def visit_cond(self, cond_block):
        for condition, block in cond_block.branches:
            if self.eval(condition):
                self._set_ret_value(self.eval(block))
                break

    def visit_for(self, for_block):
        item_var_name = for_block.item_ident.get_name()
        try:
            items = list(self.eval(for_block.list_expr))
        except TypeError:
            raise Exception("Cannot loop over non-list")

        for_env = Environment(parent=self._env)
        interpreter = Interpreter(for_env)
        ret = None

        for item in items:
            for_env.set_value(item_var_name, item)
            if for_block.filter_cond and not interpreter.eval(for_block.filter_cond):
                continue
            block_str = None
            for block in for_block.blocks:
                block_value = interpreter.eval(block)
                if block_value is not None:
                    if block_str is None:
                        block_str = block_value
                    else:
                        block_str += block_value
            if block_str is not None:
                if ret is None:
                    ret = block_str
                else:
                    ret += os.linesep + block_str

        self._set_ret_value(ret)

    def visit_expr(self, expr):
        if isinstance(expr, SimpleValue):
            ret = expr.get_value()
        elif isinstance(expr, Identifier):
            ret = self._eval_identifier(expr)
        elif isinstance(expr, QualifiedName):
            ret = self._eval_qualified_name(expr)
        else:
            raise Exception(f"Line {expr.token.line_num}: Unsupported expression {expr.token.lexeme}")
        self._set_ret_value(ret)

    def visit_logical_bin(self, logical_bin):
        left = self.eval(logical_bin.left)
        op = logical_bin.op.lexeme
        if op == "or":
            if left:
                self._set_ret_value(left)  # shortcut evaluation
                return
            self._set_ret_value(self.eval(logical_bin.right))
        elif op == "and":
            if not left:
                self._set_ret_value(left)  # shortcut evaluation
                return
            self._set_ret_value(self.eval(logical_bin.right))
        else:
            raise Exception(f"Line {logical_bin.op.line_num}: Unknown operator {op}")

    def visit_logical_rel(self, logical_rel):
        left = self.eval(logical_rel.left)
        right = self.eval(logical_rel.right)
        op = logical_rel.op.lexeme
        ret = None
        if op == "==":
            ret = left == right
        elif op == "<>":
            ret = left != right
        elif op == ">":
            ret = left > right
        elif op == ">=":
            ret = left >= right
        elif op == "<":
            ret = left < right
        elif op == "<=":
            ret = left <= right
        else:
            raise Exception(f"Line {logical_rel.op.line_num}: Unknown operator {op}")
        self._set_ret_value(ret)

    def visit_negation(self, negation):
        ret = not self.eval(negation.expr)
        self._set_ret_value(ret)

    def _eval_identifier(self, expr):
        name = expr.get_name()
        value = self._env.get_value(name)
        if value is None:
            raise Exception(f"Line {expr.token.line_num}: Identifier {name} is not defined")
        return value

    def _eval_qualified_name(self, expr):
        path = [tok.lexeme for tok in expr.identifier_tokens]
        value = self._env.get_value(path[0])
        for component in path[1:]:
            value = getattr(value, component)
        return value
