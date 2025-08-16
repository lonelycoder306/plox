from LoxCallable import LoxCallable
from Stmt import Stmt
from Environment import Environment
from Error import Return

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment, 
                 isInitializer: bool):
        self.declaration = declaration
        self.closure = closure
        self.isInitializer = isInitializer
    
    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.isInitializer)
    
    def call(self, interpreter, expr, arguments):
        environment = Environment(self.closure)

        for i in range(0, len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        
        from Token import Token, TokenType
        dummyToken = Token(TokenType.THIS, "this", None, 0, 0)

        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as r:
            if self.isInitializer:
                return self.closure.getAt(0, dummyToken)

            return r.value
        
        if self.isInitializer:
            return self.closure.getAt(0, dummyToken)
    
    def arity(self):
        return len(self.declaration.params)
    
    def toString(self):
        if self.declaration.name == None:
            return "<lambda>"
        return f"<fn {self.declaration.name.lexeme}>"