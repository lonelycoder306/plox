from LoxCallable import LoxCallable
from Error import RuntimeError

class ListFunction(LoxCallable):
    def __init__(self, mode):
        self.mode = mode
        self.instance = None
    
    def bind(self, instance):
        self.instance = instance
    
    def check(self, expr, arguments):
        pass

    def call(self, interpreter, expr, arguments):
        match self.mode:
            case "printList":
                self.l_print()
            case "first":
                return self.l_first()
    
    def l_print(self):
        print(self.instance)
    
    def l_first(self):
        return self.instance.array[0]

    def arity(self):
        match self.mode:
            case "printList":
                return 0
            case "first":
                return 0

functions = ["printList", "first"]

class List:
    def __init__(self, array: list):
        self.array = array
        self.methods = dict()
        for function in functions:
            self.methods[function] = ListFunction(function)

    def get(self, name):
        method = self.methods.get(name.lexeme, None)
        if method != None:
            import copy
            func = copy.deepcopy(method)
            func.bind(self)
            return func
        
        raise RuntimeError(name, f"Undefined property or method '{name.lexeme}'.")

    def set():
        pass

    def __str__(self):
        from Interpreter import Interpreter
        dummyInterpreter = Interpreter()
        string = "["
        for element in self.array:
            string += dummyInterpreter.stringify(element) + ", "
        if string[-2:] == ", ":
            string = string[:-2]
        string += "]"
        return string

# To have a List() constructor function.
# Alternative way of creating/declaring a list.
class ListInit(LoxCallable):
    def bind(self, instance):
        self.instance = instance
    
    def check(self, arguments, expr):
        if type(arguments[0]) == List:
            return True
        raise RuntimeError(expr.callee.name, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: list.")

    def call(self, interpreter, expr, arguments):
        if self.check(arguments, expr):
            return List(arguments[0].array)

    def arity(self):
        return 1

initList = ListInit()