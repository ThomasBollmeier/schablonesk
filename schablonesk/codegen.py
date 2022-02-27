from schablonesk.scanner import Scanner
from schablonesk.parser import Parser
from schablonesk.environment import Environment
from schablonesk.interpreter import Interpreter
from schablonesk.template_exports import TemplateExports


def generate_code(template_code, **params):
    ast = Parser(Scanner().scan(template_code)).parse()

    env = Environment()
    for name, value in params.items():
        env.set_value(name, value)

    return Interpreter(env, TemplateExports()).eval(ast)

