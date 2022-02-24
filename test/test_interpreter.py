import os
import unittest

from schablonesk.scanner import Scanner
from schablonesk.parser import Parser
from schablonesk.environment import Environment
from schablonesk.interpreter import Interpreter


class _Person(object):

    def __init__(self, last_name, first_name):
        self.last_name = last_name
        self.first_name = first_name


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

    def test_qualified_name(self):

        global_env = Environment()
        global_env.set_value("ego", _Person("Bollmeier", "Thomas"))
        interpreter = Interpreter(global_env)

        code = "$(ego.first_name)"
        ast = self.create_parser(code).parse()
        value = interpreter.eval(ast)

        self.assertEqual(value, "Thomas")

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

    def test_disjunction(self):

        global_env = Environment()
        global_env.set_value("a", 42)
        global_env.set_value("b", 23)
        interpreter = Interpreter(global_env)

        code = ":> a == 42 or b == 23"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)

        code = ":> a <> 42 or b == 23"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)

        code = ":> a == 42 or b <> 23"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)

        code = ":> a <> 42 or b <> 23"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertFalse(value)

    def test_conjunction(self):

        global_env = Environment()
        global_env.set_value("a", 42)
        global_env.set_value("b", 23)
        interpreter = Interpreter(global_env)

        code = ":> a == 42 and b == 23"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertTrue(value)

        code = ":> a <> 42 and b == 23"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertFalse(value)

        code = ":> a == 42 and b <> 23"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertFalse(value)

        code = ":> a <> 42 and b <> 23"
        ast = self.create_parser(code)._logical_expr()
        value = interpreter.eval(ast)

        self.assertTrue(isinstance(value, bool))
        self.assertFalse(value)

    def test_text(self):

        global_env = Environment()
        global_env.set_value("last_name", "Mustermann")
        global_env.set_value("first_name", "Herbert")
        interpreter = Interpreter(global_env)

        code = "Guten Tag, $( first_name) $(last_name)!"
        ast = self.create_parser(code).parse()
        value = interpreter.eval(ast)

        self.assertEqual(value, "Guten Tag, Herbert Mustermann!")

    def test_cond_block(self):

        global_env = Environment()
        global_env.set_value("input", 42)
        global_env.set_value("someone_asked", True)
        interpreter = Interpreter(global_env)

        code = """:> cond 
            :> input == 42
                :> cond someone_asked
        The answer to everything: $(input).
                :> endcond
            :> else
        Some random number ($(input)).
        :> endcond"""

        ast = self.create_parser(code).parse()
        value = interpreter.eval(ast)

        self.assertEqual(value.strip(), "The answer to everything: 42.")

    def test_for_block(self):

        global_env = Environment()
        global_env.set_value("numbers", [1, 2, 3])
        interpreter = Interpreter(global_env)

        code = """:> for number in numbers
            :> cond number <> 2
        The number is $(number).
            :> endcond
        :> endfor"""

        ast = self.create_parser(code).parse()
        value = interpreter.eval(ast)

        expected = [
            "The number is 1.",
            "The number is 3."
        ]
        actual = [line.strip() for line in value.split(os.linesep)]

        self.assertEqual(expected, actual)

    def test_snippet_call(self):

        global_env = Environment()
        global_env.set_value("numbers", [1, 2, 3])
        interpreter = Interpreter(global_env)

        code = """:> snippet number_info (n)
        The number is: $(n).
        :> endsnippet
        :> for number in numbers where number <> 2
            :> paste number_info(number)
        :> endfor"""

        ast = self.create_parser(code).parse()
        value = interpreter.eval(ast)

        expected = [
            "The number is: 1.",
            "The number is: 3."
        ]
        actual = [line.strip() for line in value.split(os.linesep)]

        self.assertEqual(expected, actual)
