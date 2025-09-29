from __future__ import annotations
from typing import Any

from Token import Token
from Error import RuntimeError

class Environment:
    def __init__(self, enclosing: Environment | None = None) -> None:
        self.enclosing = enclosing
        self.values: dict[str, Any] = {}
        self.access: dict[str, str] = {}
    
    def get(self, name: Token) -> Any | None:
        if name.lexeme in self.values.keys():
            value = self.values.get(name.lexeme)
            # Tuple-type value -> variable is uninitialized.
            if type(value) != tuple:
                return value
            
            raise RuntimeError(name, f"Uninitialized variable or function '{name.lexeme}'.")
        
        elif self.enclosing != None:
            return self.enclosing.get(name)
        
        raise RuntimeError(name, f"Undefined variable or function '{name.lexeme}'.")
    
    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values.keys():
            if self.access[name.lexeme] == "FIX":
                raise RuntimeError(name, f"Fixed variable '{name.lexeme}' cannot be re-assigned.")
            self.values[name.lexeme] = value
            return
        
        if self.enclosing != None:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    
    def define(self, name: str, value: Any, access: str) -> None:
        self.values[name] = value
        self.access[name] = access

    def ancestor(self, distance: int):
        environment = self
        for i in range(0, distance):
            environment = environment.enclosing
        return environment
    
    def getAt(self, distance: int, name: Token) -> Any | None:
        return self.ancestor(distance).get(name)

    def assignAt(self, distance: int, name: Token, value: Any) -> None:
        self.ancestor(distance).assign(name, value)