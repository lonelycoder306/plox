from Error import RuntimeError
from LoxFunction import LoxFunction

class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.private = dict()
        self.public = dict()
        self.fields = self.private

    def get(self, name):
        import State

        if name.lexeme in self.private.keys():
            if State.inMethod and (State.currentClass == self.klass):
                return self.private[name.lexeme]
            raise RuntimeError(name, f"Private field '{name.lexeme}' is inaccessible.")

        if name.lexeme in self.public.keys():
            return self.public[name.lexeme]
        
        method = self.klass.findMethod(name.lexeme, name)
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
        self.fields[name.lexeme] = value
    
    def toString(self, interpreter, expr = None, arguments = None):
        method = self.klass.findMethod("_str")
        if method != None:
            return method.bind(self).call(interpreter, expr, arguments)
        return f"<{self.klass.name} instance>"

    def varType(self):
        return self.klass.name

from LoxCallable import LoxCallable
class InstanceFunction(LoxCallable):
    def __init__(self, mode: str):
        self.mode = mode
    
    def bind(self, instance: LoxInstance):
        self.instance = instance

    def call(self, interpreter, expr, arguments):
        match self.mode:
            case "_fieldList":
                return self.i_fieldList(interpreter, expr, arguments)
            case "_methodList":
                return self.i_methodList(interpreter, expr, arguments)
            case "_fields":
                self.i_fields(interpreter, expr, arguments)
                return ()
            case "_methods":
                self.i_methods(interpreter, expr, arguments)
                return ()
    
    def i_fieldList(self, interpreter, expr, arguments):
        privates = list(self.instance.private.keys())
        publics = list(self.instance.public.keys())
        array = publics + privates
        from List import List
        return List(array)

    def i_methodList(self, interpreter, expr, arguments):
        private = self.instance.klass.private.keys()
        public = self.instance.klass.public.keys()
        array = list(private + public)
        from List import List
        return List(array)

    def i_fields(self, interpreter, expr, arguments):
        privates = self.instance.private
        for field in privates.keys():
            print(f"{field}: private")
        publics = self.instance.public
        for field in publics.keys():
            if isinstance(publics[field], LoxCallable):
                continue
            value = interpreter.stringify(publics[field])
            print(f"{field}: {value}")
    
    def i_methods(self, interpreter, expr, arguments):
        private = self.instance.klass.private
        for method in private.keys():
            value = interpreter.stringify(private[method])
            print(f"{method}: {value}")
        public = self.instance.klass.public
        for method in public.keys():
            value = interpreter.stringify(public[method])
            print(f"{method}: {value}")
    
    def arity(self):
        match self.mode:
            case "_fieldList":
                return [0,0]
            case "_methodList":
                return [0,0]
            case "_fields":
                return [0,0]
            case "_methods":
                return [0,0]
    
    def toString(self):
        return f"<native method {self.mode}>"