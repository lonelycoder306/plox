from Expr import Expr
from LoxInstance import LoxInstance
from Token import Token

# Warning raised if code appears after return statement within the same scope.
class returnWarning(Warning):
    def __init__(self, token: Token) -> None:
        self.token = token # The token appearing after the return statement.
        self.message = "code found after return statement (will be ignored).\n"
    def warn(self) -> None:
        from LoxMain import warn
        warn(self)

class unusedWarning(Warning):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.message = "unused local variable found.\n"
    def warn(self) -> None:
        from LoxMain import warn
        warn(self)

class UserWarning(Warning):
    def __init__(self, warning: LoxInstance, expression: Expr) -> None:
        self.warning = warning
        self.expression = expression
    
    def show(self, interpreter) -> None:
        method = self.warning.klass.findMethod("show")
        method.bind(self.warning).call(interpreter,
                                     self.expression,
                                     [])