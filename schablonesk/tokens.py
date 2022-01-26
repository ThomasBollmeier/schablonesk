class Token(object):
    TEXT = 1
    IDENTIFIER = 2
    UNKNOWN = 99

    def __init__(self, category, lexeme):
        self.category = category
        self.lexeme = lexeme
