from Token import Token

class BaseError(Exception):
    def show(self):
        from LoxMain import error
        error(self)

class ScanError(BaseError):
    def __init__(self, line: int, column: int, file: str, message: str):
        self.line = line
        self.column = column
        self.file = file
        self.message = message

class ParseError(BaseError):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message

class StaticError(BaseError):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message

class RuntimeError(BaseError):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message

# Not actual errors.
class BreakError(Exception):
    def __init__(self, token, loopType):
        self.token = token
        self.loopType = loopType

class ContinueError(Exception):
    def __init__(self, token, loopType):
        self.token = token
        self.loopType = loopType

class Return(Exception):
    def __init__(self, value):
        self.value = value

class StopError(Exception):
    pass

class UserError(Exception):
    def __init__(self, error, expression):
        self.error = error
        self.expression = expression
    
    def show(self, interpreter):
        method = self.error.klass.findMethod("show")
        method.bind(self.error).call(interpreter,
                                     self.expression,
                                     [])