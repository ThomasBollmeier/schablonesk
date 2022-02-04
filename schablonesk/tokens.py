class Token(object):

    def __init__(self, category, lexeme, line_num):
        self.category = category
        self.lexeme = lexeme
        self.line_num = line_num
