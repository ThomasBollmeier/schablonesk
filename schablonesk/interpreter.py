import os
from schablonesk.ast import *
from schablonesk.config import Config
from schablonesk.scanner import Scanner
from schablonesk.parser import Parser, IndentationUnit
from schablonesk.environment import Environment
from schablonesk.template_exports import TemplateExports


class Interpreter(BaseVisitor):

    def __init__(self, environment, template_exports=TemplateExports([os.curdir])):
        BaseVisitor.__init__(self)
        self._env = environment
        self._template_exports = template_exports
        self._stack = []

    def eval(self, ast):
        self._stack.append(None)
        ast.accept(self)
        return self._stack.pop()

    def _set_ret_value(self, value):
        self._stack[-1] = value

    def visit_template(self, templ):
        ret = ""
        for usage in templ.usages:
            usage.accept(self)
        for snippet in templ.snippets:
            snippet.accept(self)
        for block in templ.blocks:
            if ret:
                ret += os.linesep
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
        interpreter = Interpreter(for_env, self._template_exports)
        ret = None

        last_idx = len(items) - 1
        for idx, item in enumerate(items):
            for_env.set_value(item_var_name, item)
            for_env.set_value("is_first", idx == 0)
            for_env.set_value("is_last", idx == last_idx)
            if for_block.filter_cond and not interpreter.eval(for_block.filter_cond):
                continue
            block_str = self._eval_blocks(for_block.blocks, interpreter)
            if block_str is not None:
                if ret is None:
                    ret = block_str
                else:
                    ret += os.linesep + block_str

        self._set_ret_value(ret)

    def visit_assignment(self, assignment):
        value = self.eval(assignment.source)
        name = assignment.target.lexeme
        self._env.set_value(name, value)
        self._set_ret_value("")

    @staticmethod
    def _eval_blocks(blocks, interpreter):
        ret = None
        for block in blocks:
            block_value = interpreter.eval(block)
            if block_value is not None:
                if ret is None:
                    ret = block_value
                elif block_value:
                    ret += os.linesep + block_value
        return ret

    def visit_snippet(self, snippet):
        snippet_name = snippet.name.lexeme
        self._env.set_value(snippet_name, snippet)

    def visit_snippet_call(self, snippet_call):
        snippet_name = snippet_call.name.lexeme

        snippet = self._env.get_value(snippet_name)
        if snippet is None:
            raise Exception(f"Unknown snippet {snippet_name}")

        num_args = len(snippet_call.args)
        num_params = len(snippet.params)
        if num_args != num_params:
            raise Exception(f"#args (={num_args}) does not match #params (={num_params})")

        arg_values = [self.eval(arg) for arg in snippet_call.args]
        snippet_env = Environment()
        for i, param in enumerate(snippet.params):
            snippet_env.set_value(param.lexeme, arg_values[i])

        interpreter = Interpreter(snippet_env, self._template_exports)
        ret = self._eval_blocks(snippet.blocks, interpreter)

        if snippet_call.indent:
            value_expr, unit = snippet_call.indent
            value = self.eval(value_expr)
            if not isinstance(value, int):
                raise Exception("Indentation value must be an integer")
            indent = "\t" * value if unit == IndentationUnit.TABS else " " * value
            ret = os.linesep.join([indent + line for line in ret.split(os.linesep)])

        self._set_ret_value(ret)

    def visit_call(self, func_call):
        callee = self.eval(func_call.callee)
        arg_values = [self.eval(arg) for arg in func_call.args]
        self._set_ret_value(callee(*arg_values))

    def visit_use(self, use):
        templ_name = self.eval(use.template_name)
        templ_exports = self._template_exports.get_exports(templ_name)
        if use.names:
            for (name_id, alias_id) in use.names:
                name = name_id.lexeme
                alias = alias_id is not None and alias_id.lexeme or None
                if name not in templ_exports:
                    raise Exception(f"'{name}' is not provided by '{templ_name}'")
                if alias is None:
                    self._env.set_value(name, templ_exports[name])
                else:
                    self._env.set_value(alias, templ_exports[name])
        else:
            for name, ast in templ_exports.items():
                self._env.set_value(name, ast)

    def visit_expr(self, expr):
        if isinstance(expr, String):
            ret = expr.get_value().replace("\\'", "'")[1:-1]
        elif isinstance(expr, SimpleValue):
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
