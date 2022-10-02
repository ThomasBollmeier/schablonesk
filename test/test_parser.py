import os
import unittest

from schablonesk.ast_printer import AstPrinter
from schablonesk.scanner import Scanner
from schablonesk.parser import Parser


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.scanner = Scanner()

    def test_parse_for_stmt(self):
        code = """
        :> for item in list
            :> cond  
                :> is_first
        print("List")
            :> endcond
        print("Item")
        :> endfor
        """
        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_for_stmt_with_filter(self):
        code = """
        :> for item in list where item.has_todo == true or day > 5
        print("Item")
        :> endfor
        """
        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_left_assign(self):
        code = ":> answer <- 42"

        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_right_assign(self):
        code = ":> 42 -> answer"

        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_assignment_in_block(self):
        code = """
        :> for state in states
            :> cond 
                :> state
                    :> block
                        :> status_text <- 'open'
                        :> button_text <- 'Set to done'
                    :> endblock
                :> else
                    :> block
                        :> status_text <- 'done'
                        :> button_text <- 'Reopen'
                    :> endblock
            :> endcond
            $(status_text) 
        :> endfor
        """
        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_logical_expr(self):
        code = """
        :> cond not (a <> zero) and (b == one or c <= two)
        print("OK")
        :> endcond
        """
        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_snippet(self):
        code = """:> snippet say_hello (greeting name) 
         $(greeting) $(name)!
         :> endsnippet
         :> paste say_hello('Hallo' 'Thomas')"""

        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_paste_snippet_w_tab_indent(self):
        code = """:> snippet say_hello (greeting name) 
         $(greeting) $(name)!
         :> endsnippet
         :> paste say_hello('Hallo' 'Thomas') indent by 1 tabs"""

        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_paste_snippet_w_space_indent(self):
        code = """:> snippet say_hello (greeting name) 
         $(greeting) $(name)!
         :> endsnippet
         :> paste say_hello('Hallo' 'Thomas') indent by 4 spaces"""

        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_call(self):
        code = ":> add(1 sub(43 2))"

        ast = Parser(self.scanner.scan(code)).parse_expr()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_use_all(self):
        code = ":> use 'my_standard'"

        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_use_some_snippets(self):
        code = ":> use head(header) footer from 'my_standard'"

        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_file(self):
        file_path = os.path.dirname(__file__) + "/demo.schablonesk"
        code = self._read_file(file_path)

        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    @staticmethod
    def _read_file(file_path):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        return "".join(lines)


if __name__ == "__main__":
    unittest.main()
