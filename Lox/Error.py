from __future__ import annotations
from typing import Any, TYPE_CHECKING

from Expr import Expr
from Token import Token

if TYPE_CHECKING:
    from Interpreter import Interpreter
    from LoxInstance import LoxInstance

class BaseError(Exception):
    def show(self) -> None:
        from LoxMain import error
        error(self)

class ScanError(BaseError):
    def __init__(self, line: int, column: int, file: str, message: str) -> None:
        self.line = line
        self.column = column
        self.file = file
        self.message = message

class ParseError(BaseError):
    def __init__(self, token: Token, message: str) -> None:
        self.token = token
        self.message = message

class StaticError(BaseError):
    def __init__(self, token: Token, message: str) -> None:
        self.token = token
        self.message = message

class RuntimeError(BaseError):
    def __init__(self, token: Token, message: str) -> None:
        self.token = token
        self.message = message

# Not actual errors.
class BreakError(Exception):
    def __init__(self, token: Token, loopType: str) -> None:
        self.token = token
        self.loopType = loopType

class ContinueError(Exception):
    def __init__(self, token: Token, loopType: str) -> None:
        self.token = token
        self.loopType = loopType

class Return(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value

class StopError(Exception):
    pass

class UserError(Exception):
    def __init__(self, error: LoxInstance, expression: Expr) -> None:
        self.error = error
        self.expression = expression
    
    def show(self, interpreter: Interpreter) -> None:
        method = self.error.klass.findMethod("show")
        assert (method != None)
        method.bind(self.error).call(interpreter,
                                     self.expression,
                                     [])