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

    def eval(self, template_ast):
        ret = ""
        for block in template_ast.blocks:
            ret += self._eval_block(block)
        return ret

    def _eval_block(self, ast):
        if isinstance(ast, Text):
            return self._eval_text(ast)
        elif isinstance(ast, CondBlock):
            return self._eval_cond_block(ast)
        elif isinstance(ast, ForBlock):
            return self._eval_for_block(ast)
        else:
            raise Exception("Unsupported evaluation")

    def eval_expr(self, expr):
        if isinstance(expr, SimpleValue):
            return expr.get_value()
        elif isinstance(expr, Identifier):
            return self._eval_identifier(expr)
        elif isinstance(expr, QualifiedName):
            return self._eval_qualified_name(expr)
        elif isinstance(expr, Negation):
            return self._eval_negation(expr)
        elif isinstance(expr, LogicalRelation):
            return self._eval_logical_rel(expr)
        elif isinstance(expr, LogicalBinExpr):
            return self._eval_logical_bin(expr)
        else:
            raise Exception(f"Line {expr.token.line_num}: Unsupported expression {expr.token.lexeme}")

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

    def _eval_logical_rel(self, logical_rel):
        left = self.eval_expr(logical_rel.left)
        right = self.eval_expr(logical_rel.right)
        op = logical_rel.op.lexeme
        if op == "==":
            return left == right
        elif op == "<>":
            return left != right
        elif op == ">":
            return left > right
        elif op == ">=":
            return left >= right
        elif op == "<":
            return left < right
        elif op == "<=":
            return left <= right
        else:
            raise Exception(f"Line {logical_rel.op.line_num}: Unknown operator {op}")

    def _eval_logical_bin(self, logical_bin):
        left = self.eval_expr(logical_bin.left)
        op = logical_bin.op.lexeme
        if op == "or":
            if left:
                return left  # shortcut evaluation
            return self.eval_expr(logical_bin.right)
        elif op == "and":
            if not left:
                return left  # shortcut evaluation
            return self.eval_expr(logical_bin.right)
        else:
            raise Exception(f"Line {logical_bin.op.line_num}: Unknown operator {op}")

    def _eval_negation(self, negation):
        return not self.eval_expr(negation.expr)

    def _eval_text(self, text):
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
                    ret += str(self.eval_expr(ast))
                    search_pos = pos + len(end)
                else:
                    ret += content[search_pos:]
                    break
            else:
                ret += content[search_pos:]
                break
        return ret

    def _eval_cond_block(self, cond_block):
        for condition, block in cond_block.branches:
            if self.eval_expr(condition):
                return self._eval_block(block)
        return None

    def _eval_for_block(self, for_block):
        item_var_name = for_block.item_ident.get_name()
        try:
            items = list(self.eval_expr(for_block.list_expr))
        except TypeError:
            raise Exception("Cannot loop over non-list")

        for_env = Environment(parent=self._env)
        interpreter = Interpreter(for_env)
        ret = None

        for item in items:
            for_env.set_value(item_var_name, item)
            # TODO: make use of filter condition
            block_str = None
            for block in for_block.blocks:
                block_value = interpreter._eval_block(block)
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

        return ret
