import os
import unittest

from schablonesk.scanner import Scanner
from schablonesk.parser import Parser
from schablonesk.environment import Environment
from schablonesk.interpreter import Interpreter
from schablonesk.template_exports import TemplateExports


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

    def test_for_block_first_last(self):

        global_env = Environment()
        global_env.set_value("numbers", [1, 2, 3])
        interpreter = Interpreter(global_env)

        code = """:> for number in numbers
            :> cond is_first or is_last
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

    def test_left_assign(self):

        global_env = Environment()
        interpreter = Interpreter(global_env)
        code = """:> answer <- 42
The answer to everything is $(answer)."""

        ast = self.create_parser(code).parse()
        actual = interpreter.eval(ast)

        self.assertEqual("The answer to everything is 42.", actual)

        self.assertEqual(42, global_env.get_value("answer"))

    def test_right_assign(self):
        global_env = Environment()
        interpreter = Interpreter(global_env)
        code = """:> 42 -> answer
The answer to everything is $(answer)."""

        ast = self.create_parser(code).parse()
        actual = interpreter.eval(ast)

        self.assertEqual("The answer to everything is 42.", actual)

        self.assertEqual(42, global_env.get_value("answer"))

    def test_assignment_in_block(self):
        global_env = Environment()
        global_env.set_value("states", [False, True])
        global_env.set_value("add1", lambda i: i + 1)
        interpreter = Interpreter(global_env)

        code = """
            :> for state in states
            :> cond 
                :> not state
                    :> block
                        :> status_text <- 'open'
                        :> label <- 'set to done'
                    :> endblock
                :> else
                    :> block
                        :> status_text <- 'done'
                        :> label <- 'reopen'
                    :> endblock
            :> endcond
$(status_text), $(label)
:> endfor"""

        ast = self.create_parser(code).parse()
        value = interpreter.eval(ast)

        expected = [
            "open, set to done",
            "done, reopen"
        ]
        actual = list(filter(lambda line: bool(line), value.split(os.linesep)))

        self.assertEqual(expected, actual)

    def test_snippet_call(self):

        global_env = Environment()
        global_env.set_value("numbers", [1, 2, 3])
        interpreter = Interpreter(global_env)

        code = """:> snippet number_info (n)
The number is: $(n).
        :> endsnippet
        :> for number in numbers where number <> 2
            :> paste number_info(number) indent by 4 spaces
        :> endfor"""

        ast = self.create_parser(code).parse()
        value = interpreter.eval(ast)

        expected = [
            "    The number is: 1.",
            "    The number is: 3."
        ]
        actual = value.split(os.linesep)

        self.assertEqual(expected, actual)

    def test_call(self):

        def add(a, b):
            return a + b

        def sub(a, b):
            return a - b

        global_env = Environment()
        global_env.set_value("add", add)
        global_env.set_value("sub", sub)
        interpreter = Interpreter(global_env)

        code = ":> add(1 sub(43 2))"

        ast = self.create_parser(code).parse_expr()
        value = interpreter.eval(ast)

        self.assertEqual(42, value)

    def test_use_statement(self):

        global_env = Environment()

        templ_exports = TemplateExports([os.curdir])
        templ_code = """
        :> snippet h1_element(text)
        <h1>$(text)</h1>
        :> endsnippet
        """
        templ_exports.set_template_code("base", templ_code)

        interpreter = Interpreter(global_env, templ_exports)

        code = """:> use h1_element(title) from 'base'
        :> paste title('Hallo Welt!')"""

        ast = self.create_parser(code).parse()
        value = interpreter.eval(ast)

        self.assertEqual(value.strip(), "<h1>Hallo Welt!</h1>")

