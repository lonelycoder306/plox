from typing import Any, Literal, NoReturn
from LoxInstance import LoxInstance
from Token import Token
from Environment import Environment
from Error import RuntimeError

class LoxGroup(LoxInstance):
    def __init__(self, name: str, environment: Environment) -> None:
        self.name = name
        self.environment = environment
    
    def get(self, name: Token) -> Any | None:
        if name.lexeme in self.environment.values.keys():
            value = self.environment.values.get(name.lexeme)
            if type(value) != tuple:
                return value
            else:
                raise RuntimeError(name, f"Uninitialized member '{name.lexeme}'.")
        else:
            raise RuntimeError(name, f"'{name.lexeme}' is not a member of group '{self.name}'.")
    
    def set(self, name: Token, value: Any, access: str) -> NoReturn:
        raise RuntimeError(name, "Cannot re-assign namespace members.")
    
    def varType(self) -> str:
        return "group"

    def toString(self) -> str:
        return f"<group {self.name}>"