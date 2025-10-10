from __future__ import annotations
from typing import Any, TYPE_CHECKING, Literal, Never

from Error import RuntimeError
from List import List
from LoxFunction import LoxFunction
from Expr import Expr
from Token import TokenType
from String import String
import State

if TYPE_CHECKING:
    from Interpreter import Interpreter
    from LoxClass import LoxClass
    from LoxInstance import LoxInstance
    from Token import Token

class LoxInstance:
    def __init__(self, klass: LoxClass) -> None:
        self.klass = klass
        self.private: dict[str, Any] = {}
        self.public: dict[str, Any] = {}

    def verifyClass(self, klass: LoxClass) -> bool:
        while klass != None:
            if klass == State.currentClass:
                return True
            klass = klass.superclass
        return False

    def get(self, name: Token) -> Any | LoxFunction:
        if name.lexeme in self.private.keys():
            if State.inMethod and self.verifyClass(self.klass):
                return self.private[name.lexeme]
            raise RuntimeError(name, f"Private field '{name.lexeme}' is inaccessible.")

        if name.lexeme in self.public.keys():
            return self.public[name.lexeme]
        
        method = self.klass.findMethod(name.lexeme, name)
        if method != None:
            if type(method) == LoxFunction:
                return method.bind(self)
            elif isinstance(method, LoxCallable):
                import copy
                func = copy.deepcopy(method)
                func.bind(self)
                return func
        
        raise RuntimeError(name, f"Undefined property or method '{name.lexeme}'.")
    
    def set(self, name: Token, value: Any, visibility: str):
        if name.lexeme in self.private.keys():
            if State.inMethod and self.verifyClass(self.klass):
                self.private[name.lexeme] = value
                return
            raise RuntimeError(name, f"Private field '{name.lexeme}' is inaccessible.")
        tempMethod = self.klass.findMethod(name.lexeme)
        if tempMethod != None:
            raise RuntimeError(name, f"Method in class definition cannot be re-assigned.")
        
        if visibility == "private":
            self.private[name.lexeme] = value
        elif visibility == "public":
            self.public[name.lexeme] = value
    
    def toString(self, interpreter: Interpreter, 
                    expr: None = None, arguments: list = []) -> String | str:
        method = self.klass.findMethod("_str")
        if method != None:
            if method.arity() != [0,0]:
                token = method.declaration.params[0]
                if type(token) == Expr.Assign:
                    token = token.name
                raise RuntimeError(token, "_str method must take no arguments.")
            string = method.bind(self).call(interpreter, expr, arguments)
            if type(string) != String:
                raise RuntimeError(method.declaration.name, 
                                   "_str method does not return a string.")
            return string
        return f"<{self.klass.name} instance>"

    def varType(self) -> str:
        return self.klass.name + " instance"

    def compareMethodStr(self, expr: Expr.Binary) -> str:
        match expr.operator.type:
            case TokenType.GREATER:
                return "_gt"
            case TokenType.GREATER_EQUAL:
                return "_ge"
            case TokenType.LESS:
                return "_lt"
            case TokenType.LESS_EQUAL:
                return "_le"
            case TokenType.BANG_EQUAL:
                return "_ne"
            case TokenType.EQUAL_EQUAL:
                return "_eq"

    def compare(self, other: LoxInstance, interpreter: Interpreter, 
                    expr: Expr.Binary) -> bool | tuple:
        methodTitle = self.compareMethodStr(expr)
        method = self.klass.findMethod(methodTitle)
        if method != None:
            if method.arity() != [1,1]:
                token = method.declaration.name
                if len(method.declaration.params) != 0:
                    token = method.declaration.params[0]
                if type(token) == Expr.Assign:
                    token = token.name
                raise RuntimeError(token, f"{methodTitle} method must take no arguments.")
            value = method.bind(self).call(interpreter, expr, [other])
            if type(value) != bool:
                raise RuntimeError(method.declaration.name, 
                                   f"{methodTitle} method does not return a Boolean value.")
            return value
        else:
            return ()

from LoxCallable import LoxCallable
class InstanceFunction(LoxCallable):
    def __init__(self, mode: str) -> None:
        self.mode: str = mode
        self.instance: LoxInstance | None = None
    
    def bind(self, instance: LoxInstance) -> None:
        self.instance = instance

    def call(self, interpreter: Interpreter, expr: Expr, 
                arguments: list[Any]) -> List | tuple | None:
        if self.instance == None:
            # Expr is a Call Expr.
            # The Call Expr's callee is a Get Expr.
            # The Get Expr's object is a Variable Expr.
            raise RuntimeError(expr.callee.object.name, 
                               "Can only retrieve fields or methods for class instances.")

        match self.mode:
            case "_fieldList":
                return self.i_fieldList()
            case "_methodList":
                return self.i_methodList()
            case "_fields":
                self.i_fields(interpreter)
                return ()
            case "_methods":
                self.i_methods(interpreter)
                return ()
    
    def i_fieldList(self) -> List:
        privates = list(self.instance.private.keys())
        publics = list(self.instance.public.keys())
        array = publics + privates
        return List(array)

    def i_methodList(self) -> List:
        privates = list(self.instance.klass.private.keys())
        publics = list(self.instance.klass.public.keys())
        array = list(privates + publics)
        return List(array)

    def i_fields(self, interpreter: Interpreter) -> None:
        privates = self.instance.private
        for field in privates.keys():
            print(f"{field}: private")
        publics = self.instance.public
        for field in publics.keys():
            if isinstance(publics[field], LoxCallable):
                continue
            value = interpreter.stringify(publics[field])
            print(f"{field}: {value}")
    
    def i_methods(self, interpreter: Interpreter) -> None:
        private = self.instance.klass.private
        for method in private.keys():
            value = interpreter.stringify(private[method])
            print(f"{method}: {value}")
        public = self.instance.klass.public
        for method in public.keys():
            value = interpreter.stringify(public[method])
            print(f"{method}: {value}")
    
    def arity(self) -> list[int]:
        match self.mode:
            case "_fieldList":
                return [0,0]
            case "_methodList":
                return [0,0]
            case "_fields":
                return [0,0]
            case "_methods":
                return [0,0]
    
    def toString(self) -> str:
        return f"<native method {self.mode}>"