from schablonesk.parser import Parser
from schablonesk.scanner import Scanner


class TemplateExports(object):

    def __init__(self):
        self._exports = {}

    def set_template_code(self, template_name, code):
        template_ast = Parser(Scanner().scan(code)).parse()
        if template_ast is None:
            raise Exception(f"Cannot parse template {template_name}")
        all_exports = dict(
            [(snippet.name.lexeme, snippet) for snippet in template_ast.snippets]
        )
        self._exports[template_name] = all_exports

    def get_exports(self, template_name, used_names=[]):
        if template_name not in self._exports:
            self._load(template_name)

        all_exports = self._exports[template_name]
        if not used_names:
            return all_exports
        else:
            return dict([(name, all_exports[name])
                         for name in used_names
                         if name in all_exports])

    def _load(self, template_name):
        raise Exception("Not yet implemented")

