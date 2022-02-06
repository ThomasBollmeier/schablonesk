import unittest
import os.path
from schablonesk.scanner import Scanner


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
        self.assertEqual(len(tokens), 17)

        for token in tokens:
            catg = token.category
            lexeme = token.lexeme
            line_num = token.line_num
            print(f"@line {line_num}: <<{lexeme}>> ({catg})")

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
