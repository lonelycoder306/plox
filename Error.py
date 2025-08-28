from Token import Token

class LexError(Exception):
    def __init__(self, line: int, column: int, file: str, message: str):
        self.line = line
        self.column = column
        self.file = file
        self.message = message
    def show(self):
        from Lox import lError
        lError(self)

class ParseError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
    def show(self):
        from Lox import tError
        tError(self)

class ResolveError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
    def show(self):
        from Lox import tError
        tError(self)

class RuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
    def show(self):
        from Lox import runtimeError
        runtimeError(self)

# Not actual errors.
class breakError(Exception):
    def __init__(self, token, loopType):
        self.token = token
        self.loopType = loopType

class continueError(Exception):
    def __init__(self, token, loopType):
        self.token = token
        self.loopType = loopType

class Return(Exception):
    def __init__(self, value):
        self.value = value

class StopError(Exception):
    pass