class Environment(object):

    def __init__(self, parent=None):
        self._parent = parent
        self._values = {}

    def set_value(self, name, value):
        self._values[name] = value

    def get_value(self, name):
        if name in self._values:
            return self._values[name]
        elif self._parent is not None:
            return self._parent.get_value(name)
        else:
            return None

