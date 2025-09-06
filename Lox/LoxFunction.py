from LoxCallable import LoxCallable
from Expr import Expr
from Stmt import Stmt
from Environment import Environment
from Error import Return
from Token import Token, TokenType
from List import List

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
        vargs = []

        if self.declaration.params != None:
            argLen = len(arguments)
            paramLen = len(self.declaration.params)
            for i in range(0, argLen):
                param = self.declaration.params[i]
                if type(param) == Token:
                    if param.type != TokenType.ELLIPSIS:
                        environment.define(param.lexeme, arguments[i])
                    else:
                        vargs = arguments[i:argLen]
                        break
                elif type(param) == Expr.Assign:
                    name = param.name
                    value = arguments[i]
                    environment.define(name.lexeme, value)
            # Will never have default parameters and variable-length parameter lists.
            # Any combination including both will throw a parse error.
            if not self.context["variadic"]:
                for i in range(argLen, paramLen):
                    name = self.declaration.params[i].name
                    value = interpreter.evaluate(self.declaration.params[i].value)
                    environment.define(name.lexeme, value)
        
        if self.context["variadic"]:
            environment.define("vargs", List(vargs))
        
        dummyToken = Token(TokenType.THIS, "this", None, 0, 0, None)

        import State as State
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
        if self.context["variadic"]:
            min -= 1 # ... must be excluded.
            max = 256
        return [min, max]
    
    def isGetter(self):
        return (self.declaration.params == None)
    
    def toString(self):
        if self.declaration.name == None:
            return "<lambda>"
        elif self.context["isMethod"]:
            return f"<method {self.declaration.name.lexeme}>"
        return f"<fn {self.declaration.name.lexeme}>"