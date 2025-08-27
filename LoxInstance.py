from Error import RuntimeError
from LoxFunction import LoxFunction

class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.private = dict()
        self.public = dict()

    def get(self, name):
        import State

        if name.lexeme in self.private.keys():
            if State.inMethod:
                return self.private[name.lexeme]
            raise RuntimeError(name, f"Private field '{name.lexeme}' is inaccessible.")

        if name.lexeme in self.public.keys():
            return self.public[name.lexeme]
        
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
        import State

        if name.lexeme in self.private.keys():
            if State.inMethod:
                self.private[name.lexeme] = value
                return
            raise RuntimeError(name, f"Private field '{name.lexeme}' is inaccessible.")
        tempMethod = self.klass.findMethod(name.lexeme)
        if tempMethod != None:
            raise RuntimeError(name, f"Method in class definition cannot be re-assigned.")
        self.public[name.lexeme] = value
    
    def toString(self, interpreter, expr = None, arguments = None):
        method = self.klass.findMethod("_str")
        if method != None:
            return method.bind(self).call(interpreter, expr, arguments)
        return f"<{self.klass.name} instance>"

    def varType(self):
        return self.klass.name