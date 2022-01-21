import unittest
from schablonesk.scanner import Scanner


class ScannerTest(unittest.TestCase):

    def setUp(self):
        self.scanner = Scanner()

    def test__scan_lines(self):
        code = """
        :> for item in items
            :> case item.id
                :> 1)
        print("1st item")
                :> *)
        print("Something else")
        print("...")
            :> endcase
        :> endfor
        """
        lines = code.split("\n")
        blocks = self.scanner._scan_lines(lines)

        self.assertEquals(len(blocks), 7)
