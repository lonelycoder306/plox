from Lox.Token import Token
from Lox.Error import RuntimeError

class Environment:
    def __init__(self, enclosing = None):
        self.enclosing = enclosing
        self.values = dict()
    
    def get(self, name: Token):
        if name.lexeme in self.values.keys():
            value = self.values.get(name.lexeme)
            # Tuple-type value -> variable is uninitialized.
            if type(value) != tuple:
                return value
            
            raise RuntimeError(name, f"Uninitialized variable or function '{name.lexeme}'.")
        
        elif self.enclosing != None:
            return self.enclosing.get(name)
        
        raise RuntimeError(name, f"Undefined variable or function '{name.lexeme}'.")
    
    def assign(self, name: Token, value):
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return
        
        if self.enclosing != None:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    
    def define(self, name, value):
        self.values[name] = value

    def ancestor(self, distance: int):
        environment = self
        for i in range(0, distance):
            environment = environment.enclosing
        return environment
    
    def getAt(self, distance: int, name: Token):
        return self.ancestor(distance).get(name)

    def assignAt(self, distance: int, name: Token, value):
        self.ancestor(distance).assign(name, value)