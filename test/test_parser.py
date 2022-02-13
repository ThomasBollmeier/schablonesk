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
        :> for item in list where item.has_todo or day > five
        print("Item")
        :> endfor
        """
        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)

    def test_parse_logical_expr(self):
        code = """
        :> cond a <> zero and (b == one or c <= two)
        print("OK")
        :> endcond
        """
        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)


if __name__ == "__main__":
    unittest.main()
