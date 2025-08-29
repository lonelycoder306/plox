from LoxCallable import LoxCallable
from LoxInstance import LoxInstance
from Error import RuntimeError

class LoxClass(LoxInstance, LoxCallable):
    def __init__(self, metaclass, superclass, name: str, private: dict, public: dict):
        super().__init__(metaclass)
        self.superclass = superclass
        self.name = name
        self.private = private
        self.public = public
    
    def call(self, interpreter, expr, arguments):
        from LoxInstance import LoxInstance
        instance = LoxInstance(self)
        initializer = self.findMethod("init")
        if initializer != None:
            instance.fields = instance.private
            initializer.bind(instance).call(interpreter, expr, arguments)
        instance.fields = instance.public
        return instance
    
    def findMethod(self, nameString, nameToken = None):
        if nameString in self.private.keys():
            import State
            if State.inMethod:
                method = self.private.get(nameString)
                if method.context["class"].name == self.name:
                    return method
            raise RuntimeError(nameToken, f"Private method '{nameString}' is inaccessible.")
        
        elif nameString in self.public.keys():
            return self.public.get(nameString)
        
        elif self.superclass != None:
            return self.superclass.findMethod(nameString, nameToken)
        
        return None
    
    def arity(self):
        initializer = self.findMethod("init")
        if initializer == None:
            return [0,0]
        return initializer.arity()
    
    def toString(self):
        return f"<class {self.name}>"