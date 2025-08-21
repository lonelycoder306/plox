from LoxCallable import LoxCallable
from LoxInstance import LoxInstance

class LoxClass(LoxInstance, LoxCallable):
    def __init__(self, metaclass, name: str, methods: dict):
        super().__init__(metaclass)
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
        return self.methods.get(name, None)
    
    def arity(self):
        initializer = self.findMethod("init")
        if initializer == None:
            return 0
        return initializer.arity()
    
    def toString(self):
        return f"<class {self.name}>"