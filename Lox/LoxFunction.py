from Lox.LoxCallable import LoxCallable
from Lox.Expr import Expr
from Lox.Stmt import Stmt
from Lox.Environment import Environment
from Lox.Error import Return
from Lox.Token import Token, TokenType

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment, 
                 context: dict):
        self.declaration = declaration
        self.closure = closure
        self.context = context
    
    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        method = LoxFunction(self.declaration, environment, self.context)
        return method
    
    def call(self, interpreter, expr, arguments):
        environment = Environment(self.closure)

        if self.declaration.params != None:
            argLen = len(arguments)
            paramLen = len(self.declaration.params)
            for i in range(0, argLen):
                param = self.declaration.params[i]
                if type(param) == Token:
                    environment.define(param.lexeme, arguments[i])
                elif type(param) == Expr.Assign:
                    name = param.name
                    value = arguments[i]
                    environment.define(name.lexeme, value)
            for i in range(argLen, paramLen):
                name = self.declaration.params[i].name
                value = interpreter.evaluate(self.declaration.params[i].value)
                environment.define(name.lexeme, value)
        
        dummyToken = Token(TokenType.THIS, "this", None, 0, 0, None)

        import Lox.State as State
        currentState = State.inMethod
        currentClass = State.currentClass

        try:
            if self.context["isMethod"]:
                State.inMethod = True
                State.currentClass = self.context["class"]
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as r:
            State.callStack = State.callStack[1:]
            # Reset inMethod.
            if self.context["isMethod"]:
                State.inMethod = currentState
                State.currentClass = currentClass
            if self.context["isInitializer"]:
                return self.closure.getAt(0, dummyToken)
            return r.value
        
        State.callStack = State.callStack[1:]
        # Reset inMethod.
        if self.context["isMethod"]:
            State.inMethod = currentState
            State.currentClass = currentClass
        if self.context["isInitializer"]:
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
        elif self.context["isMethod"]:
            return f"<method {self.declaration.name.lexeme}>"
        return f"<fn {self.declaration.name.lexeme}>"