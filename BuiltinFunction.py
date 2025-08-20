from LoxCallable import LoxCallable
from Environment import Environment
from Error import RuntimeError
from List import List
from Expr import Expr

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
# 5. length(x) - Returns the length of a string (other iterable data types to be added).
# 6. strformat(x) - Returns an ASCII-encoded/formatted version of its argument string.
# 7. breakpoint() - Starts a debug prompt when run from a file.

builtins = Environment()
functions = ["clock", "type", "string", "number", "length", "strformat", "perror", "breakpoint"]

class BuiltinFunction(LoxCallable):
    def __init__(self, mode: str):
        self.mode = mode
    
    def call(self, interpreter, expr, arguments):
        if self.mode == "clock":
            return self.b_clock()
        if self.mode == "type":
            return self.b_type(interpreter, arguments[0])
        if self.mode == "string":
            return self.b_string(interpreter, arguments[0])
        if self.mode == "number":
            return self.b_number(arguments[0], expr)
        if self.mode == "length":
            return self.b_length(arguments[0], expr)
        if self.mode == "strformat":
            return self.b_strformat(arguments[0], expr)
        if self.mode == "perror":
            self.b_perror(arguments[0], expr)
        if self.mode == "breakpoint":
            self.b_breakpoint(interpreter)
    
    def b_clock(self):
        from datetime import datetime
        return datetime.now().time()
    
    def b_type(self, interpreter, object):
        return f"<{interpreter.varType(object)}>"
    
    def b_string(self, interpreter, object):
        return interpreter.stringify(object)
    
    def b_number(self, object, expr):
        callee = None
        if type(expr.callee) == Expr.Variable:
            callee = expr.callee.name
        elif type(expr.callee) == Expr.Access:
            callee = expr.leftParen
        for char in object:
            if not (char.isdigit() or (char == '.') or (char in ['+', '-'])):
                raise RuntimeError(callee, "Invalid input to number().")
        return float(object)
    
    def b_length(self, object, expr):
        callee = None
        if type(expr.callee) == Expr.Variable:
            callee = expr.callee.name
        elif type(expr.callee) == Expr.Access:
            callee = expr.leftParen
        validTypes = (str, List)
        if type(object) not in validTypes: # Will work for strings (other data types to be added).
            raise RuntimeError(callee, "Invalid input to length().")
        if type(object) == str:
            return float(len(object))
        elif type(object) == List:
            return float(len(object.array))
    
    def b_strformat(self, object, expr):
        callee = None
        if type(expr.callee) == Expr.Variable:
            callee = expr.callee.name
        elif type(expr.callee) == Expr.Access:
            callee = expr.leftParen
        if type(object) != str:
            raise RuntimeError(callee, "strformat() only accepts string arguments.")
        return object.encode("utf-8").decode("unicode_escape")
     
    def b_perror(self, message, expr):
        if type(message) != str:
            raise RuntimeError(expr.rightParen, "perror() only accepts string arguments.")
        import sys
        sys.stderr.write(message + '\n')
    
    def b_breakpoint(self, interpreter):
        from Debug import breakpointStop
        raise breakpointStop(interpreter, interpreter.environment)

    def arity(self):
        if self.mode == "clock":
            return 0
        if self.mode == "type":
            return 1
        if self.mode == "string":
            return 1
        if self.mode == "number":
            return 1
        if self.mode == "length":
            return 1
        if self.mode == "strformat":
            return 1
        if self.mode == "perror":
            return 1
        if self.mode == "breakpoint":
            return 0 # breakpointStop's constructor takes one argument, but the user breakpoint() function takes none.

    def toString(self):
        return "<native fn>"
    
def builtinSetUp():
    for function in functions:
        builtins.define(function, BuiltinFunction(function))