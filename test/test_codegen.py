import os
import unittest
from schablonesk.codegen import generate_code


class Person(object):

    def __init__(self, name, first_name, age):
        self.name = name
        self.first_name = first_name
        self.age = age


class CodegenTest(unittest.TestCase):

    def test_codegen(self):
        file_path = os.path.dirname(__file__) + "/list.schablonesk"
        template_code = self._read_file(file_path)
        people = [
            Person("Mustermann", "Herbert", 55),
            Person("Mustermann", "Willi", 5),
            Person("Mustermann", "Erika", 42),
        ]

        generated = generate_code(template_code, people=people)

        print(generated)

    def test_codegen_with_use(self):
        file_path = os.path.dirname(__file__) + "/index.html.schablonesk"
        template_code = self._read_file(file_path)

        generated = generate_code(
            template_code,
            title="My most beloved Hobbies",
            hobbies=["Hacking", "Running", "Reading"]
        )

        print(generated)

    @staticmethod
    def _read_file(file_path):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        return "".join(lines)
