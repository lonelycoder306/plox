from Error import RuntimeError

class List:
    def __init__(self, array: list):
        self.array = array

    def __str__(self):
        string = "["
        for element in self.array:
            string += str(element) + ", "
        if string[-2:] == ", ":
            string = string[:-2]
        string += "]"
        return string

from LoxCallable import LoxCallable
class ListInit(LoxCallable):
    def bind(self, instance):
        self.instance = instance
    
    def check(self, arguments, expr):
        if type(arguments[0]) == list:
            return True
        elif type(arguments[0]) == List:
            return True
        raise RuntimeError(expr.callee.name, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: list.")

    def call(self, interpreter, expr, arguments):
        if self.check(arguments, expr):
            if type(arguments[0]) == list:
                return List(arguments[0])
            elif type(arguments[0]) == List:
                return List(arguments[0].array)

    def arity(self):
        return 1

initList = ListInit()