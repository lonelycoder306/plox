from LoxCallable import LoxCallable
from Stmt import Stmt
from Environment import Environment
from Error import Return

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment):
        self.declaration = declaration
        self.closure = closure
    
    def call(self, interpreter, expr, arguments):
        environment = Environment(self.closure)

        for i in range(0, len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        
        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as r:
            return r.value
    
        return None
    
    def arity(self):
        return len(self.declaration.params)
    
    def toString(self):
        if self.declaration.name == None:
            return "<lambda>"
        return f"<fn {self.declaration.name.lexeme}>"