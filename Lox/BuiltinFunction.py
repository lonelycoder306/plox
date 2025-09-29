from __future__ import annotations
from typing import Any, TYPE_CHECKING

from datetime import datetime, time
from Environment import Environment
from Error import RuntimeError
from Expr import Expr
from List import List
from LoxCallable import LoxCallable
from LoxInstance import LoxInstance
from Reference import Reference
from String import String

if TYPE_CHECKING:
    from Interpreter import Interpreter

# General class to implement built-in functions.

'''
To define a built-in function, simply include its logic under its mode for both call() and arity(), 
constructing a method for it that is used for call(), and then create a BuiltinFunction object 
with the appropriate mode. You thereafter assign the appropriate name to the object in 
the builtins environment.
'''

# Current built-in functions supported:
# 1. clock() - Prints the current time.
# 2. type(x) - Prints the type of x.
# 3. str(x) - Returns a string form of x.
# 4. number(x) - Returns a number (float) form of x.
# 5. length(x) - Returns the length of a string (String object) or list (List object).
# 6. copy(x) - Returns an isolated copy of X (will use the constructor if X is a class instance).
# 7. strformat(x) - Returns an ASCII-encoded/formatted version of its argument string.
# 8. perror(x) - Prints message X to stderr.
# 9. arity(x) - Returns the arity of function X.
# 10. reference(x) - Returns a reference to the exact object passed to it.
# Similar to C++, this allows assignment or argument passing for functions
# to use the object itself, rather than a copy (which is the default).
# Once the return value of the function is used somewhere, e.g., assigned to a variable,
# passed to a function, etc., it simply becomes the object.
# Until then, it is a Reference object.
# 11. breakpoint() - Starts a debug prompt when run from a file.

builtins = Environment()
functions = ["clock", "type", "string", "number", "length", "copy",
            "strformat", "perror", "arity", "reference", "breakpoint", "debug"]

class BuiltinFunction(LoxCallable):
    def __init__(self, mode: str) -> None:
        self.mode: str = mode
    
    def call(self, interpreter: Interpreter, expr: Expr.Call, 
             arguments: list[Any]) -> Any:
        if self.mode == "clock":
            return self.b_clock()
        if self.mode == "type":
            return self.b_type(interpreter, arguments[0])
        if self.mode == "string":
            return self.b_string(interpreter, arguments[0])
        if self.mode == "number":
            return self.b_number(expr, arguments[0])
        if self.mode == "length":
            return self.b_length(expr, arguments[0])
        if self.mode == "copy":
            return self.b_copy(interpreter, expr, arguments)
        if self.mode == "strformat":
            return self.b_strformat(expr, arguments[0])
        if self.mode == "perror":
            if len(arguments) == 2:
                self.b_perror(expr, arguments[0], arguments[1])
            elif len(arguments) == 1:
                self.b_perror(expr, arguments[0])
            return ()
        if self.mode == "arity":
            return self.b_arity(expr, arguments[0])
        if self.mode == "reference":
            return self.b_reference(arguments[0])
        if self.mode == "breakpoint":
            self.b_breakpoint(interpreter, expr)
            return ()
        if self.mode == "debug":
            self.b_debug(interpreter)
            return ()
    
    def b_clock(self) -> time:
        return datetime.now().time()
    
    def b_type(self, interpreter: Interpreter, object: Any) -> String:
        return String(f"<{interpreter.varType(object)}>")
    
    def b_string(self, interpreter: Interpreter, object: Any) -> String:
        return String(interpreter.stringify(object))
    
    def b_number(self, expr: Expr.Call, object: Any) -> float | None:
        callee = None
        if type(expr.callee) == Expr.Variable:
            callee = expr.callee.name
        elif type(expr.callee) == Expr.Access:
            callee = expr.rightParen
        if type(object) != String:
            raise RuntimeError(callee, "Invalid input to number().")
        for char in object.text:
            if not (char.isdigit() or (char == '.') or (char in ['+', '-'])):
                raise RuntimeError(callee, "Invalid input to number().")
        return float(object.text)
    
    def b_length(self, expr: Expr.Call, object: Any) -> float | None:
        callee = None
        if type(expr.callee) == Expr.Variable:
            callee = expr.callee.name
        elif type(expr.callee) == Expr.Access:
            callee = expr.rightParen
        validTypes = (String, List)
        if type(object) not in validTypes:
            raise RuntimeError(callee, "Invalid input to length().")
        if type(object) == String:
            return float(len(object.text))
        elif type(object) == List:
            return float(len(object.array))
    
    def b_copy(self, interpreter: Interpreter, expr: Expr.Call, 
               arguments: list[Any]) -> Any:
        object = arguments[0]
        if isinstance(object, LoxInstance):
            return object.klass.call(interpreter, expr, arguments)
        import copy
        newObj = copy.deepcopy(object)
        return newObj
    
    def b_strformat(self, expr: Expr.Call, object: Any) -> String | None:
        callee = None
        if type(expr.callee) == Expr.Variable:
            callee = expr.callee.name
        elif type(expr.callee) == Expr.Access:
            callee = expr.rightParen
        if type(object) != String:
            raise RuntimeError(callee, "strformat() only accepts string arguments.")
        return String(object.text.encode("utf-8").decode("unicode_escape"))
     
    def b_perror(self, expr: Expr.Call, message: String, 
                 format: bool = True) -> None:
        if type(message) != String:
            raise RuntimeError(expr.rightParen, "perror() only accepts string arguments.")
        import sys
        if format:
            text = message.text.encode("utf-8").decode("unicode_escape")
        else:
            text = message.text
        sys.stderr.write(text + '\n')
    
    def b_arity(self, expr: Expr.Call, function: Any) -> List | None:
        if not isinstance(function, LoxCallable):
            raise RuntimeError(expr.rightParen, "arity() only accepts function arguments.")
        return List(function.arity())

    def b_reference(self, object: Any) -> Reference:
        return Reference(object)
    
    def b_breakpoint(self, interpreter: Interpreter, expr: Expr.Call) -> None:
        from Debug import breakpointStop
        breakpointStop(interpreter, interpreter.environment, expr).debugStart()
    
    def b_debug(self, interpreter: Interpreter) -> None:
        from Debug import replDebugger
        replDebugger(interpreter).runDebugger()

    def arity(self) -> list[int]:
        if self.mode == "clock":
            return [0,0]
        if self.mode == "type":
            return [1,1]
        if self.mode == "string":
            return [1,1]
        if self.mode == "number":
            return [1,1]
        if self.mode == "length":
            return [1,1]
        if self.mode == "copy":
            return [1,1]
        if self.mode == "strformat":
            return [1,1]
        if self.mode == "perror":
            return [1,2]
        if self.mode == "arity":
            return [1,1]
        if self.mode == "reference":
            return [1,1]
        if self.mode == "breakpoint":
            return [0,0] # breakpointStop's constructor takes one argument, 
                         # but the user breakpoint() function takes none.
        if self.mode == "debug":
            return [0,0]

    def toString(self) -> str:
        return "<native fn>"
    
def builtinSetUp() -> None:
    for function in functions:
        builtins.define(function, BuiltinFunction(function), "VAR")