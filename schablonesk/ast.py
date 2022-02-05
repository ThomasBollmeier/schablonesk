class Template(object):

    def __init__(self, blocks):
        self.blocks = blocks


class Text(object):

    def __init__(self, text_token):
        self._token = text_token
