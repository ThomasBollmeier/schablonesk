import unittest

from schablonesk.scanner import Scanner
from schablonesk.parser import Parser
from schablonesk.environment import Environment
from schablonesk.interpreter import Interpreter


class InterpreterTest(unittest.TestCase):

    def setUp(self):
        self.scanner = Scanner()

    def create_parser(self, code):
        return Parser(self.scanner.scan(code))

    def test_identifier(self):

        global_env = Environment()
        global_env.set_value("is_done", True)
        interpreter = Interpreter(global_env)

        code = ":> is_done"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)

    def test_equal(self):

        global_env = Environment()
        global_env.set_value("answer", 42)
        interpreter = Interpreter(global_env)

        code = ":> answer == 42"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)

    def test_not_equal(self):

        global_env = Environment()
        global_env.set_value("answer", 42)
        interpreter = Interpreter(global_env)

        code = ":> answer <> 41"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)

    def test_greater(self):

        global_env = Environment()
        global_env.set_value("answer", 42)
        interpreter = Interpreter(global_env)

        code = ":> answer > 41"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)

    def test_greater_equal(self):

        global_env = Environment()
        global_env.set_value("answer", 42)
        interpreter = Interpreter(global_env)

        code = ":> answer >= 42"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)

    def test_lesser(self):

        global_env = Environment()
        global_env.set_value("answer", 42)
        interpreter = Interpreter(global_env)

        code = ":> answer < 43"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)

    def test_lesser_equal(self):

        global_env = Environment()
        global_env.set_value("answer", 42)
        interpreter = Interpreter(global_env)

        code = ":> answer <= 42"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)

    def test_negation(self):

        global_env = Environment()
        global_env.set_value("answer", 42)
        interpreter = Interpreter(global_env)

        code = ":> not (answer == 41)"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)
