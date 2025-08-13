from Error import RuntimeError

class LoxInstance:
    from LoxClass import LoxClass
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields = dict()

    def get(self, name):
        if name.lexeme in self.fields.keys():
            return self.fields[name.lexeme]
        
        method = self.klass.findMethod(name.lexeme)
        if method != None:
            return method
        
        raise RuntimeError(name, f"Undefined property or method '{name.lexeme}'.")
    
    def set(self, name, value):
        self.fields[name.lexeme] = value
    
    def toString(self):
        return f"<{self.klass.name} instance>"