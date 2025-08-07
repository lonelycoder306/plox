from Token import Token

# Warning raised if code appears after return statement within the same scope.
class returnWarning(Warning):
    def __init__(self, token: Token):
        self.token = token # The token appearing after the return statement.
        self.message = f"code found after return statement (will be ignored).\n"
    def warn(self):
        from Lox import warn
        warn(self)

class unusedWarning(Warning):
    def __init__(self, token: Token):
        self.token = token
        self.message = f"unused local variable found.\n"
    def warn(self):
        from Lox import warn
        warn(self)