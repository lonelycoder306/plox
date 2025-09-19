from LoxInstance import LoxInstance
from Token import Token
from Error import RuntimeError

class LoxGroup(LoxInstance):
    def __init__(self, name: str, environment):
        self.name = name
        self.environment = environment
    
    def get(self, name: Token):
        if name.lexeme in self.environment.values.keys():
            value = self.environment.values.get(name.lexeme)
            if type(value) != tuple:
                return value
            else:
                raise RuntimeError(name, f"Uninitialized member '{name.lexeme}'.")
        else:
            raise RuntimeError(name, f"'{name.lexeme}' is not a member of group '{self.name}'.")
    
    def set(self, name: Token, value, access: str):
        raise RuntimeError(name, "Cannot modify namespace members.")
    
    def varType(self):
        return "group"

    def toString(self):
        return f"<group {self.name}>"