from LoxCallable import LoxCallable
from LoxInstance import LoxInstance

class LoxClass(LoxInstance, LoxCallable):
    def __init__(self, metaclass, superclass, name: str, methods: dict):
        super().__init__(metaclass)
        self.superclass = superclass
        self.name = name
        self.methods = methods
    
    def call(self, interpreter, expr, arguments):
        from LoxInstance import LoxInstance
        instance = LoxInstance(self)
        initializer = self.findMethod("init")
        if initializer != None:
            instance.fields = instance.private
            initializer.bind(instance).call(interpreter, expr, arguments)
        instance.fields = instance.public
        return instance
    
    def findMethod(self, name: str):
        if name in self.methods.keys():
            return self.methods.get(name)
        
        if self.superclass != None:
            return self.superclass.findMethod(name)
        
        return None
    
    def arity(self):
        initializer = self.findMethod("init")
        if initializer == None:
            return 0
        return initializer.arity()
    
    def toString(self):
        return f"<class {self.name}>"