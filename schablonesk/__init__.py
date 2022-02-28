import os
from schablonesk.scanner import Scanner
from schablonesk.parser import Parser
from schablonesk.environment import Environment
from schablonesk.interpreter import Interpreter
from schablonesk.template_exports import TemplateExports


class CodeGenerator(object):

    TEMPL_PATH = "SCHABLONESK_TEMPLATE_DIRS"

    def __init__(self, search_paths=None):
        if search_paths is not None:
            self._search_paths = search_paths
        elif self.TEMPL_PATH in os.environ:
            self._search_paths = os.environ[self.TEMPL_PATH].split(os.pathsep)
        else:
            self._search_paths = [os.path.curdir]

    def generate_code(self, template_code, **params):
        ast = Parser(Scanner().scan(template_code)).parse()

        env = Environment()
        for name, value in params.items():
            env.set_value(name, value)

        return Interpreter(env, TemplateExports(self._search_paths)).eval(ast)
