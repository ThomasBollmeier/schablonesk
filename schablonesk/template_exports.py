import os.path
from schablonesk.parser import Parser
from schablonesk.scanner import Scanner

TEMPL_PATH = "SCHABLONESK_TEMPLATE_DIRS"


class TemplateExports(object):

    def __init__(self):
        self._exports = {}
        self._search_paths = [os.path.curdir]
        if TEMPL_PATH in os.environ:
            add_search_paths = os.environ[TEMPL_PATH].split(os.pathsep)
            self._search_paths += add_search_paths

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
        for search_path in self._search_paths:
            template_path = os.path.join(search_path, template_name)
            if os.path.exists(template_path):
                with open(template_path, "r") as f:
                    template_code = f.read()
                    self.set_template_code(template_name, template_code)
                    return
        raise Exception(f"Cannot load template file '{template_name}'")

