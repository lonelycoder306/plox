from LoxCallable import LoxCallable
from Error import RuntimeError

class ListFunction(LoxCallable):
    def __init__(self, mode):
        self.mode = mode
        self.instance = None
    
    def bind(self, instance):
        self.instance = instance
    
    def check(self, expr, arguments):
        checkFuncString = "check_" + self.mode
        checkFunc = ListFunction.__dict__[checkFuncString]
        return checkFunc(self, expr, arguments)

    def call(self, interpreter, expr, arguments):
        match self.mode:
            # Adds element to the end of the list.
            case "add":
                self.l_add(expr, arguments[0])
            # Adds element to specified position X.
            case "insert":
                return self.l_insert(expr, arguments[0], arguments[1])
            # Removes last element and returns it.
            case "pop":
                return self.l_pop(expr)
            # Removes element at position X and returns it.
            case "remove":
                self.l_remove(expr, arguments[0])
            # Removes argument from list (if found) and returns it.
            case "delete":
                self.l_delete(expr, arguments[0], arguments[1])

            # Combines elements of the list into a single string.
            # Raises an error if any of them aren't strings.
            case "join":
                return self.l_join(expr)
            # Applies some operation to all elements.
            # Operation need not return a value.
            case "forEach":
                self.l_forEach(expr, arguments[0])
            # Applies some operation to each element, returning a new list.
            # Operation must return a value (corresponding element in the new list).
            case "transform":
                return self.l_transform(expr, arguments[0])
            # Returns a new list with only the elements satisfying some predicate.
            case "filter":
                return self.l_filter(expr, arguments[0])
            # Returns a new list containing all non-list elements.
            # List elements are replaced with their contained elements, recursively.
            case "flat": 
                return self.l_flat(expr)

            # Returns whether or not the given element is in the list.
            case "contains":
                return self.l_contains(expr, arguments[0])
            # Returns index of first occurrence of argument (-1 if not found).
            case "index":
                return self.l_index(expr, arguments[0])
            # Returns index of last occurrence of argument (-1 if not found).
            case "indexLast":
                return self.l_indexLast(expr, arguments[0])
            # Returns whether any element satisfies a certain predicate.
            case "any":
                return self.l_any(expr, arguments[0])
            # Returns whether all elements satisfy a certain predicate.
            case "all":
                return self.l_all(expr, arguments[0])
            # Returns a new list containing all the elements
            # that satisfy a particular predicate.
            case "collect":
                return self.l_collect(expr, arguments[0])
            
            # Returns a reversed form of the original list.
            case "reverse":
                return self.l_reverse(expr)
            # Returns a sorted form of the original list.
            # Can be done in ascending or descending order (Boolean parameter).
            case "sort":
                return self.l_sort(expr, arguments[0])
            # Returns whether or not the list is sorted.
            # Can check for ascending or descending order (Boolean parameter).
            case "sorted":
                return self.l_sorted(expr, arguments[0])
            # Returns a new list with index-based pairings from the instance
            # and argument.
            # Continues until one of the lists ends.
            case "pair":
                return self.l_pair(expr, arguments[0])
            # Separates a list like the form produced by pair() into two lists.
            # Raises an error(?) if a non-pair element exists in the argument.
            case "separate":
                return self.l_separate(expr)

            # Returns the sum of the elements.
            # Elements must be numeric.
            case "sum":
                return self.l_sum(expr)
            # Returns the smallest element in the list.
            # Elements must be all numeric or strings.
            # List must be homogeneous.
            case "min":
                return self.l_sum(expr)
            # Returns the largest element in the list.
            # Elements must be all numeric or strings.
            # List must be homogeneous.
            case "max":
                return self.l_max(expr)
            # Returns the average of the elements in the list.
            # Elements must be all numeric.
            case "average":
                return self.l_average(expr)
    
    def l_add(self, expr, element):
        self.instance.array.append(element)
    
    def l_insert(self, expr, index, element):
        index = int(index)
        self.instance.array.insert(index, element)

    def l_pop(self, expr):
        return self.instance.array.pop()

    def l_remove(self, expr, index):
        array = self.instance.array
        index = int(index)
        element = array[index]
        array = array[:index] + array[index + 1:]
        self.instance.array = array
        return element

    def l_delete(self, expr, element, all: bool = False):
        # Handle ValueError here.
        array = self.instance.array
        if all:
            while element in array:
                array.remove(element)
        else:
            if element in array:
                self.instance.array.remove(element)

    def l_join(self, expr):
        string = ""
        for part in self.instance.array:
            string += part
        return string

    def l_forEach(self, expr, operation):
        pass

    def l_transform(self, expr, mapping):
        pass

    def l_filter(self, expr, condition):
        pass

    def l_flat(self, expr):
        pass


    def l_contains(self, expr, element):
        return (element in self.instance.array)

    def l_index(self, expr, element):
        if element in self.instance.array:
            return float(self.instance.array.index(element))
        else:
            return float(-1)

    def l_indexLast(self, expr, element):
        import copy
        array = copy.deepcopy(self.instance.array)
        array.reverse()
        if element in array:
            return float(len(array) - array.index(element) - 1)
        else:
            return -1

    def l_any(self, expr, condition):
        pass

    def l_all(self, expr, condition):
        pass
    
    def l_collect(self, expr, condition):
        pass


    def l_reverse(self, expr):
        import copy
        array = copy.deepcopy(self.instance.array)
        array.reverse()
        return List(array)

    def l_sort(self, expr, ascending: bool):
        import copy
        array = copy.deepcopy(self.instance.array)
        array.sort(reverse = not ascending)
        return List(array)
    
    def l_sorted(self, expr, ascending: bool):
        array = self.instance.array
        for i in range(0, len(array) - 1):
            if ascending:
                if array[i] > array[i+1]:
                    return False
            else:
                if array[i] < array[i+1]:
                    return False
        return True

    def l_pair(self, expr, secondList):
        array = self.instance.array
        # Argument check before ensures secondList is a List object.
        secondList = secondList.array
        pair = []
        len1 = len(array)
        len2 = len(secondList)
        i = 0
        while (i < len1) and (i < len2):
            # Elements should be List objects, not built-in lists.
            pair.append(List([array[i], secondList[i]]))
            i += 1
        return List(pair)

    def l_separate(self, expr):
        pass


    def l_sum(self, expr):
        array = self.instance.array
        return float(sum(array))

    def l_min(self, expr):
        array = self.instance.array
        return float(min(array))

    def l_max(self, expr):
        array = self.instance.array
        return float(max(array))

    def l_average(self, expr):
        array = self.instance.array
        return float(sum(array) / len(array))

    # ------------------------------------------------------------

    def arity(self):
        match self.mode:
            case "add":
                return 1
            case "insert":
                return 2
            case "pop":
                return 0
            case "remove":
                return 1
            case "delete":
                return 2

            case "join":
                return 0
            case "forEach":
                return 1
            case "transform":
                return 1
            case "filter":
                return 1
            case "flat":
                return 0

            case "contains":
                return 1
            case "index":
                return 1
            case "indexLast":
                return 1
            case "any":
                return 1
            case "all":
                return 1
            case "collect":
                return 1

            case "reverse":
                return 0
            case "sort":
                return 1
            case "sorted":
                return 1
            case "pair":
                return 1
            case "separate":
                return 0

            case "sum":
                return 0
            case "min":
                return 0
            case "max":
                return 0
            case "average":
                return 0
    
    # ------------------------------------------------------------
    def toString(self):
        return "<list method>"

functions = ["add", "insert", "pop", "remove", "delete",
             "join", "forEach", "transform", "filter", "flat",
             "contains", "index", "indexLast", "any", "all", "collect",
             "reverse", "sort", "sorted", "pair", "separate",
             "sum", "min", "max", "average"]

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
            if type(element) == str:
                string += "\""
            string += dummyInterpreter.stringify(element)
            if type(element) == str:
                string += "\""
            string += ", "
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
        obj = arguments[0]
        argType = type(obj)
        if (argType == List) or (argType == str):
            return True
        elif argType == float:
            if int(obj) == obj:
                return True
        raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: list/string/integer.")

    def call(self, interpreter, expr, arguments):
        if self.check(arguments, expr):
            obj = arguments[0]
            if type(obj) == List:
                return List(arguments[0].array)
            elif type(obj) == str:
                return List(list(arguments[0]))
            elif type(obj) == float:
                length = int(obj)
                array = list()
                for i in range(0, length):
                    array.append(None)
                return List(array)

    def arity(self):
        return 1

initList = ListInit()