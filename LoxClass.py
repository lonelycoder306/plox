from LoxCallable import LoxCallable

class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: dict):
        self.name = name
        self.methods = methods
    
    def call(self, interpreter, expr, arguments):
        from LoxInstance import LoxInstance
        instance = LoxInstance(self)
        return instance
    
    def findMethod(self, name: str):
        return self.methods.get(name, None)
    
    def arity(self):
        return 0
    
    def toString(self):
        return f"<class {self.name}>"