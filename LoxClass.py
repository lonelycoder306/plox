from LoxCallable import LoxCallable

class LoxClass(LoxCallable):
    def __init__(self, name: str):
        self.name = name
    
    def call(self, interpreter, expr, arguments):
        from LoxInstance import LoxInstance
        instance = LoxInstance(self)
        return instance
    
    def arity(self):
        return 0
    
    def toString(self):
        return f"<class {self.name}>"