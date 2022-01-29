import unittest
from schablonesk.scanner import Scanner


class ScannerTest(unittest.TestCase):

    def setUp(self):
        self.scanner = Scanner()

    def test_scan(self):
        code = """
        :> for item in items
            :> case item.id
                :> 1)
        print("1st item")
                :> *)
        print("Something else")
        print("$(item)")
            :> endcase
        :> endfor
        """
        tokens = self.scanner.scan(code)
        self.assertEqual(len(tokens), 16)

        for token in tokens:
            catg = token.category
            lexeme = token.lexeme
            line_num = token.line_num
            print(f"@line {line_num}: <<{lexeme}>> ({catg})")

    def test__scan_lines(self):
        code = """
        :> for item in items
            :> case item.id
                :> 1)
        print("1st item")
                :> *)
        print("Something else")
        print("$(item)")
            :> endcase
        :> endfor
        """
        lines = code.split("\n")
        blocks = self.scanner._scan_lines(lines)

        self.assertEqual(len(blocks), 7)
