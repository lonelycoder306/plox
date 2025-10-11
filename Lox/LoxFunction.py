from __future__ import annotations
from typing import Any, TYPE_CHECKING

from LoxCallable import LoxCallable
from Expr import Expr
from Stmt import Stmt
from Environment import Environment
from Error import Return
from Token import Token, TokenType
from List import List

if TYPE_CHECKING:
    from Interpreter import Interpreter
    from LoxFunction import LoxFunction
    from LoxInstance import LoxInstance

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment, 
                 context: dict) -> None:
        self.declaration = declaration
        self.closure = closure
        self.context = context
        self.count = 0
        self.statics: dict[str, Any] = {}
    
    def bind(self, instance: LoxInstance) -> LoxFunction:
        environment = Environment(self.closure)
        environment.define("this", instance, "VAR")
        method = LoxFunction(self.declaration, environment, self.context)
        return method
    
    def setParams(self, interpreter: Interpreter, 
                    arguments: list[Any]) -> tuple[Environment, list[Any]]:
        environment = Environment(self.closure)
        vargs = []

        if self.declaration.params != None:
            argLen = len(arguments)
            paramLen = len(self.declaration.params)
            for i in range(0, argLen):
                param = self.declaration.params[i]
                if type(param) == Token:
                    if param.type != TokenType.ELLIPSIS:
                        environment.define(param.lexeme, arguments[i], "VAR")
                    else:
                        vargs = arguments[i:argLen]
                        break
                elif type(param) == Expr.Assign:
                    environment.define(param.name.lexeme, arguments[i], "VAR")
            # Will never have default parameters and variable-length parameter lists.
            # Any combination including both will throw a parse error.
            if not self.context["variadic"]:
                for i in range(argLen, paramLen):
                    name = self.declaration.params[i].name
                    value = interpreter.evaluate(self.declaration.params[i].value)
                    environment.define(name.lexeme, value, "VAR")
        
        return (environment, vargs)
    
    def call(self, interpreter, expr, arguments) -> Any | tuple | None:
        environment, vargs = self.setParams(interpreter, arguments)
        
        if self.context["variadic"]:
            environment.define("vargs", List(vargs), "VAR")
        
        # Add all our saved static variables to the environment.
        for var in self.statics:
            environment.define(var, self.statics[var], "VAR")
        
        dummyToken = Token(TokenType.THIS, "this", None, 0, 0, None)

        import State
        currentState = State.inMethod
        currentClass = State.currentClass
        currentFunction = State.currentFunction

        try:
            State.currentFunction = self
            if self.context["isMethod"]:
                State.inMethod = True
                State.currentClass = self.context["class"]
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as r:
            self.count += 1
            State.currentFunction = currentFunction
            State.callStack = State.callStack[1:]
            # Reset inMethod.
            if self.context["isMethod"]:
                State.inMethod = currentState
                State.currentClass = currentClass
            if self.context["isInitializer"]:
                return self.closure.getAt(0, dummyToken)
            return r.value
        
        State.currentFunction = currentFunction
        State.callStack = State.callStack[1:]
        # Reset inMethod.
        if self.context["isMethod"]:
            State.inMethod = currentState
            State.currentClass = currentClass
        if self.context["isInitializer"]:
            return self.closure.getAt(0, dummyToken)
        
        self.count += 1
        return ()
    
    def arity(self) -> list[int]:
        max = len(self.declaration.params)
        min = max - self.declaration.defaults
        if self.context["variadic"]:
            min -= 1 # ... must be excluded.
            max = 256
        return [min, max]
    
    def isGetter(self) -> bool:
        return (self.declaration.params == None)
    
    def toString(self) -> str:
        if self.declaration.name == None:
            return "<lambda>"
        elif self.context["isMethod"]:
            return f"<method {self.declaration.name.lexeme}>"
        return f"<fn {self.declaration.name.lexeme}>"