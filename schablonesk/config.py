class Config(object):

    _single = None

    @staticmethod
    def get():
        if Config._single is None:
            Config._single = Config()
        return Config._single

    def __init__(self):
        self._cmd_line_begin = ":>"
        self._templ_str_begin = "$("
        self._templ_str_end = ")"

    def get_cmd_line_begin(self):
        return self._cmd_line_begin

    def set_cmd_line_begin(self, pattern):
        self._cmd_line_begin = pattern

    def get_templ_str_delimiters(self):
        return self._templ_str_begin, self._templ_str_end

    def set_templ_str_delimiters(self, begin, end):
        self._templ_str_begin = begin
        self._templ_str_end = end
