import unittest
import os.path
from schablonesk.scanner import Scanner
from schablonesk.parser import Parser


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.scanner = Scanner()

    def test_parse(self):
        code = """
        :> if ok
        print("Sucess")
        :> else
        print("Error")
        :> endif
        """
        ast = Parser(self.scanner.scan(code)).parse()
        self.assertIsNotNone(ast)
