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
        code = """
         :> snippet say_hello (greeting name) 
         $(greeting) $(name)!
         :> endsnippet
         :> paste say_hello('Hallo' 'Thomas')
         """
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
