import unittest
import os.path
from schablonesk.scanner import Scanner
from schablonesk.token_category import *


class ScannerTest(unittest.TestCase):

    def setUp(self):
        self.scanner = Scanner()

    def test_scan(self):
        code = """
        :> for item in items
            :> cond 
                :> item.id == 1
        print("1st item")
                :> else
        print("Something else")
        print("$(item)")
            :> endcond
        :> endfor
        """
        tokens = self.scanner.scan(code)
        self.assertEqual(17, len(tokens))
        self.print_tokens(tokens)

    def test_scan_logical_expr(self):
        code = """
        :> cond a <= x and ( x < b or  y >= c ) and y < d or is_done
        print("OK")
        :> endcond
        """
        tokens = self.scanner.scan(code)
        self.assertEqual(24, len(tokens))
        self.print_tokens(tokens)

    def test_scan_paste_w_indent(self):
        code = """:> paste some_snippet() indent by 4 spaces"""
        tokens = self.scanner.scan(code)
        self.assertEqual(8, len(tokens))
        self.assertEqual(tokens[-4].category, INDENT)
        self.assertEqual(tokens[-3].category, BY)
        self.assertEqual(tokens[-1].category, SPACES)
        self.print_tokens(tokens)

    def test_scan_simple_types(self):
        code = ":> 42 23. 1.23 'O\\'Hara'"

        tokens = self.scanner.scan(code)
        self.assertEqual(4, len(tokens))
        self.print_tokens(tokens)

    @staticmethod
    def print_tokens(tokens):
        for token in tokens:
            catg = token.category
            lexeme = token.lexeme
            line_num = token.line_num
            print(f"@line {line_num}: '{lexeme}' ({catg})")

    def test_file(self):
        file_path = os.path.dirname(__file__) + "/demo.schablonesk"
        code = self._read_file(file_path)
        tokens = self.scanner.scan(code)
        self.assertEqual(len(tokens), 16)

        for token in tokens:
            catg = token.category
            lexeme = token.lexeme
            line_num = token.line_num
            print(f"@line {line_num}: <<{lexeme}>> ({catg})")

    @staticmethod
    def _read_file(file_path):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        return "".join(lines)
