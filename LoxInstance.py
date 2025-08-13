class LoxInstance:
    from LoxClass import LoxClass
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields = dict()

    def get(self, name):
        if name.lexeme in self.fields.keys():
            return self.fields[name.lexeme]
        
        raise RuntimeError(name, f"Undefined property '{name.lexeme}'.")
    
    def set(self, name, value):
        self.fields[name.lexeme] = value
    
    def toString(self):
        return f"<{self.klass.name} instance>"