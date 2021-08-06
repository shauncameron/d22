class SymbolTable:
    def __init__(self):
        self._symbols = {}

    def __call__(self, name, set=None):
        if set is None:
            return self._symbols[name] if name in self._symbols else None
        else:
            self._symbols[name] = set
            return set

    def items(self):
        return self._symbols.items()