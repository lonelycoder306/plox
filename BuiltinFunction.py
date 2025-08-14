from LoxCallable import LoxCallable
from Environment import Environment
from Error import RuntimeError

# General class to implement built-in functions.
'''
To define a built-in function, simply include its logic under its mode for both call() and arity(), 
and then create an object with the appropriate mode.
You then assign the appropriate name to the object in the variable environment.
'''

# Current built-in functions supported:
# 1. clock() - Prints the current time.
# 2. type(x) - Prints the type of x.
# 3. str(x) - Returns a string form of x.
# 4. number(x) - Returns a number (float) form of x.
# 5. breakpoint() - Starts a debug prompt when run from a file.

builtins = Environment()
functions = ["clock", "type", "str", "number", "length", "breakpoint"]

class BuiltinFunction(LoxCallable):
    def __init__(self, mode: str):
        self.mode = mode
    
    def call(self, interpreter, expr, arguments):
        if self.mode == "clock":
            return self.b_clock()
        if self.mode == "type":
            return self.b_type(interpreter, arguments[0])
        if self.mode == "str":
            return self.b_str(interpreter, arguments[0])
        if self.mode == "number":
            return self.b_number(arguments[0], expr)
        if self.mode == "length":
            return self.b_length(arguments[0], expr)
        if self.mode == "breakpoint":
            self.b_breakpoint(interpreter)
    
    def b_clock(self):
        from datetime import datetime
        return datetime.now().time()
    
    def b_type(self, interpreter, object):
        return f"<{interpreter.varType(object)}>"
    
    def b_str(self, interpreter, object):
        return interpreter.stringify(object)
    
    def b_number(self, object, expr):
        for char in object:
            if not (char.isdigit() or (char == '.') or (char in ['+', '-'])):
                raise RuntimeError(expr.callee.name, "Invalid input to number().")
        return float(object)
    
    def b_length(self, object, expr):
        if type(object) != str: # Will work for strings (other data types to be added).
            raise RuntimeError(expr.callee.name, "Invalid input to length().")
        return len(object)
    
    def b_breakpoint(self, interpreter):
        from Debug import breakpointStop
        raise breakpointStop(interpreter, interpreter.environment)

    def arity(self):
        if self.mode == "clock":
            return 0
        if self.mode == "type":
            return 1
        if self.mode == "str":
            return 1
        if self.mode == "number":
            return 1
        if self.mode == "length":
            return 1
        if self.mode == "breakpoint":
            return 0 # breakpointStop's constructor takes one argument, but the user breakpoint() function takes none.

    def toString(self):
        return "<native fn>"
    
def builtinSetUp():
    for function in functions:
        builtins.define(function, BuiltinFunction(function))