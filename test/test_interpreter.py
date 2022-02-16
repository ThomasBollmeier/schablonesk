import unittest

from schablonesk.scanner import Scanner
from schablonesk.parser import Parser
from schablonesk.environment import Environment
from schablonesk.values import *
from schablonesk.interpreter import Interpreter


class InterpreterTest(unittest.TestCase):

    def setUp(self):
        self.scanner = Scanner()

    def create_parser(self, code):
        return Parser(self.scanner.scan(code))

    def test_identifier(self):

        global_env = Environment()
        global_env.set_value("is_done", BoolValue(True))
        interpreter = Interpreter(global_env)

        code = ":> is_done"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, BoolValue))
        self.assertTrue(value.bool_value)
