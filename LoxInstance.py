from Error import RuntimeError
from LoxFunction import LoxFunction

class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = dict()

    def get(self, name):
        if name.lexeme in self.fields.keys():
            return self.fields[name.lexeme]
        
        method = self.klass.findMethod(name.lexeme)
        if method != None:
            if type(method) == LoxFunction:
                return method.bind(self)
            else:
                import copy
                func = copy.deepcopy(method)
                func.bind(self)
                return func
        
        raise RuntimeError(name, f"Undefined property or method '{name.lexeme}'.")
    
    def set(self, name, value):
        self.fields[name.lexeme] = value
    
    def toString(self, interpreter, expr = None, arguments = None):
        method = self.klass.findMethod("str")
        if method != None:
            return method.bind(self).call(interpreter, expr, arguments)
        return f"<{self.klass.name} instance>"

    def varType(self):
        return self.klass.name