from LoxCallable import LoxCallable
from Stmt import Stmt
from Environment import Environment
from Error import Return

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment, 
                 isMethod: bool, isInitializer: bool):
        self.declaration = declaration
        self.closure = closure
        self.isMethod = isMethod
        self.isInitializer = isInitializer
    
    def bind(self, instance):
        import State
        State.inMethod = True
        environment = Environment(self.closure)
        environment.define("this", instance)
        method = LoxFunction(self.declaration, environment, self.isMethod, self.isInitializer)
        method.instance = instance
        return method
    
    def call(self, interpreter, expr, arguments):
        environment = Environment(self.closure)

        if self.declaration.params != None:
            for i in range(0, len(self.declaration.params)):
                environment.define(self.declaration.params[i].lexeme, arguments[i])
        
        from Token import Token, TokenType
        dummyToken = Token(TokenType.THIS, "this", None, 0, 0, None)

        import State
        currentState = State.inMethod

        try:
            interpreter.executeBlock(self.declaration.body, environment)
            if self.isMethod:
                State.inMethod = True
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
        return len(self.declaration.params)
    
    def isGetter(self):
        return (self.declaration.params == None)
    
    def toString(self):
        if self.declaration.name == None:
            return "<lambda>"
        elif self.isMethod:
            return f"<method {self.declaration.name.lexeme}>"
        return f"<fn {self.declaration.name.lexeme}>"