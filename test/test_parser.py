import unittest

from schablonesk.ast_printer import AstPrinter
from schablonesk.scanner import Scanner
from schablonesk.parser import Parser


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.scanner = Scanner()

    def test_parse(self):
        code = """
        :> cond 
            :> ok
        print("Success")
            :> else
        print("Error")
        :> endcond
        :> cond is_first
        print("Header")
        :> endcond
        """
        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)

        AstPrinter().print(ast)


if __name__ == "__main__":
    unittest.main()
