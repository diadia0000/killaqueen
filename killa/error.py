# error.py — Killa error system


class KillaError(Exception):
    """Base class for all Killa errors."""
    pass


class KillaSyntaxError(KillaError):
    def __init__(self, message, lineno=None, position=None):
        super().__init__(message)
        self.lineno = lineno
        self.position = position

    def __str__(self):
        loc = f" at line {self.lineno}, pos {self.position}" if self.lineno and self.position else ""
        return f"SyntaxError{loc}: {self.args[0]}"


class KillaRuntimeError(KillaError):
    def __init__(self, message):
        super().__init__(f"RuntimeError: {message}")


class KillaReturn(Exception):
    """Internal flow control to return from functions."""
    def __init__(self, value):
        self.value = value
