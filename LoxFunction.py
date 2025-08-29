from LoxCallable import LoxCallable
from Expr import Expr
from Stmt import Stmt
from Environment import Environment
from Error import Return
from Token import Token, TokenType

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment, 
                 isMethod: bool, isInitializer: bool):
        self.declaration = declaration
        self.closure = closure
        self.isMethod = isMethod
        self.isInitializer = isInitializer
    
    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        method = LoxFunction(self.declaration, environment, self.isMethod, self.isInitializer)
        return method
    
    def call(self, interpreter, expr, arguments):
        environment = Environment(self.closure)

        if self.declaration.params != None:
            argLen = len(arguments)
            paramLen = len(self.declaration.params)
            for i in range(0, argLen):
                param = self.declaration.params[i]
                if type(param) == Token:
                    environment.define(self.declaration.params[i].lexeme, arguments[i])
                elif type(param) == Expr.Assign:
                    name = self.declaration.params[i].name
                    value = arguments[i]
                    environment.define(name.lexeme, value)
            for i in range(argLen, paramLen):
                name = self.declaration.params[i].name
                value = interpreter.evaluate(self.declaration.params[i].value)
                environment.define(name.lexeme, value)
        
        dummyToken = Token(TokenType.THIS, "this", None, 0, 0, None)

        import State
        currentState = State.inMethod

        try:
            if self.isMethod:
                State.inMethod = True
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as r:
            # Reset inMethod.
            if self.isMethod:
                State.inMethod = currentState
            if self.isInitializer:
                return self.closure.getAt(0, dummyToken)
            return r.value
        
        # Reset inMethod.
        if self.isMethod == True:
            State.inMethod = currentState
        if self.isInitializer:
            return self.closure.getAt(0, dummyToken)
        
        return ()
    
    def arity(self):
        max = len(self.declaration.params)
        min = max - self.declaration.defaults
        return [min, max]
    
    def isGetter(self):
        return (self.declaration.params == None)
    
    def toString(self):
        if self.declaration.name == None:
            return "<lambda>"
        elif self.isMethod:
            return f"<method {self.declaration.name.lexeme}>"
        return f"<fn {self.declaration.name.lexeme}>"