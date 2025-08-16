from LoxCallable import LoxCallable

class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: dict):
        self.name = name
        self.methods = methods
    
    def call(self, interpreter, expr, arguments):
        from LoxInstance import LoxInstance
        instance = LoxInstance(self)
        initializer = self.findMethod("init")
        if initializer != None:
            initializer.bind(instance).call(interpreter, arguments)
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