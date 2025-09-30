from __future__ import annotations
from typing import Any, TYPE_CHECKING

from Error import RuntimeError
from LoxCallable import LoxCallable
from LoxFunction import LoxFunction
from LoxInstance import LoxInstance
from Token import Token

if TYPE_CHECKING:
    from Expr import Expr
    from Interpreter import Interpreter
    from LoxClass import LoxClass

class LoxClass(LoxInstance, LoxCallable):
    def __init__(self, metaclass: LoxClass, superclass: LoxClass, 
                 name: str, private: dict[str, LoxFunction], 
                 public: dict[str, LoxFunction]) -> None:
        super().__init__(metaclass)
        self.superclass = superclass
        self.name = name
        self.private = private
        self.public = public
    
    def call(self, interpreter: Interpreter, expr: Expr, 
                arguments: list[Any]) -> LoxInstance:
        instance = LoxInstance(self)
        initializer = self.findMethod("init")
        if initializer != None:
            initializer.bind(instance).call(interpreter, expr, arguments)
        return instance
    
    def findMethod(self, nameString: str, 
                    nameToken: Token | None = None) -> LoxFunction | None:
        if nameString in self.private.keys():
            import State as State
            if State.inMethod:
                method = self.private.get(nameString)
                assert (method != None)
                if method.context["class"].name == self.name:
                    return method
            assert (nameToken != None)
            raise RuntimeError(nameToken, f"Private method '{nameString}' is inaccessible.")
        
        elif nameString in self.public.keys():
            return self.public.get(nameString)
        
        elif self.superclass != None:
            return self.superclass.findMethod(nameString, nameToken)
        
        return #None
    
    def arity(self) -> list[int]:
        initializer = self.findMethod("init")
        if initializer == None:
            return [0,0]
        return initializer.arity()
    
    def toString(self) -> str:
        return f"<class {self.name}>"