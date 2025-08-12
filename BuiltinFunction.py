from LoxCallable import LoxCallable

# General class to implement built-in functions.
'''
To define a built-in function, simply include its logic under its mode for both call() and arity(), and then create an object with the appropriate name and mode. You then assign the same name to the object in the variable environment.
'''

# Current built-in functions supported:
# 1. clock() - Prints the current time.
# 2. type(x) - Prints the type of x.
# 3. str(x) - Returns a string form of x.

class BuiltinFunction(LoxCallable):
    def __init__(self, mode): # Specify mode type (str).
        self.mode = mode
    
    def call(self, interpreter, expr, arguments):
        if self.mode == "clock":
            from datetime import datetime
            return datetime.now().time()
        if self.mode == "type":
            return f"<{interpreter.varType(arguments[0])}>"
        if self.mode == "str":
            return interpreter.stringify(arguments[0])
        if self.mode == "breakpoint":
            from Debug import breakpointStop
            raise breakpointStop(interpreter, interpreter.environment)
    
    def arity(self):
        if self.mode == "clock":
            return 0
        if self.mode == "type":
            return 1
        if self.mode == "str":
            return 1
        if self.mode == "breakpoint":
            return 0 # breakpointStop's constructor takes one argument, but the user breakpoint() function takes none.

    def toString(self):
        return "<native fn>"