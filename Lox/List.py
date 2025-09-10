from LoxCallable import LoxCallable
from Error import RuntimeError
from String import String

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
        if self.check(expr, arguments):
            match self.mode:
                # Adds element to the end of the list.
                case "add":
                    self.l_add(expr, arguments[0])
                    return ()
                # Adds element to specified position X.
                case "insert":
                    self.l_insert(expr, arguments[0], arguments[1])
                    return ()
                # Removes last element and returns it.
                case "pop":
                    return self.l_pop(expr)
                # Removes element at position X and returns it.
                case "remove":
                    return self.l_remove(expr, arguments[0])
                # Removes argument from list (if found) and returns it.
                case "delete":
                    if len(arguments) == 2:
                        self.l_delete(expr, arguments[0], arguments[1])
                    elif len(arguments) == 1:
                        self.l_delete(expr, arguments[0])
                    return ()

                # Combines elements of the list into a single string.
                # Raises an error if any of them aren't strings.
                case "join":
                    return self.l_join(expr)
                # Returns a new list with any duplicates in the original removed.
                case "unique":
                    return self.l_unique(expr)
                # Applies some operation to all elements.
                # Operation need not return a value.
                case "forEach":
                    self.l_forEach(expr, interpreter, arguments[0])
                    return ()
                # Applies some operation to each element, returning a new list.
                # Operation must return a value (corresponding element in the new list).
                case "transform":
                    return self.l_transform(expr, interpreter, arguments[0])
                # Returns a new list with only the elements satisfying some predicate.
                case "filter":
                    return self.l_filter(expr, interpreter, arguments[0])
                # Returns a new list containing all non-list elements.
                # List elements are replaced with their contained elements, recursively.
                case "flat": 
                    return self.l_flat(expr)

                # Returns whether or not the given element is in the list.
                case "contains":
                    return self.l_contains(expr, arguments[0])
                # Returns whether or not the list contains any duplicates.
                case "duplicate":
                    return self.l_duplicate(expr)
                # Returns index of first occurrence of argument (-1 if not found).
                case "index":
                    return self.l_index(expr, arguments[0])
                # Returns index of last occurrence of argument (-1 if not found).
                case "indexLast":
                    return self.l_indexLast(expr, arguments[0])
                # Returns whether any element satisfies a certain predicate.
                case "any":
                    return self.l_any(expr, interpreter, arguments[0])
                # Returns whether all elements satisfy a certain predicate.
                case "all":
                    return self.l_all(expr, interpreter, arguments[0])
                
                # Returns a reversed form of the original list.
                case "reverse":
                    return self.l_reverse(expr)
                # Returns a sorted form of the original list.
                # Can be done in ascending or descending order (Boolean parameter).
                case "sort":
                    if len(arguments) == 1:
                        return self.l_sort(expr, arguments[0])
                    elif len(arguments) == 0:
                        return self.l_sort(expr)
                # Returns whether or not the list is sorted.
                # Can check for ascending or descending order (Boolean parameter).
                case "sorted":
                    if len(arguments) == 1:
                        return self.l_sorted(expr, arguments[0])
                    elif len(arguments) == 0:
                        return self.l_sorted(expr)
                # Returns a new list with index-based pairings from the instance
                # and argument.
                # Continues until one of the lists ends.
                case "pair":
                    return self.l_pair(expr, arguments[0])
                # Separates a list like the form produced by pair() into two lists.
                # Returns a list containing the two lists.
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
        if len(self.instance.array) == 0:
            return #None
        return self.instance.array.pop()

    def l_remove(self, expr, index):
        # Check index validity before running this.
        array = self.instance.array
        index = int(index)
        element = array[index]
        array = array[:index] + array[index + 1:]
        self.instance.array = array
        return element

    def compareHelper(self, object, element) -> bool:
        if type(object) != type(element):
            return False
        match object:
            case String():
                return (object.text == element.text)
            case List():
                objArray = object.array
                elemArray = element.array
                for i, x in enumerate(objArray):
                    if not self.compareHelper(x, elemArray[i]):
                        return False
                return True
            case _:
                return (object == element)

    def l_delete(self, expr, element, all: bool = False):
        # Handle ValueError here.
        array = self.instance.array
        removed = False
        if all:
            while not removed:
                removed = True
                for object in array:
                    if self.compareHelper(object, element):
                        removed = False
                        array.remove(object)
        else:
            for object in array:
                if self.compareHelper(object, element):
                    array.remove(object)

    def l_join(self, expr):
        string = ""
        for part in self.instance.array:
            string += part.text
        return String(string)
    
    def l_unique(self, expr):
        array = self.instance.array
        uniqueArray = list(set(array))
        return List(uniqueArray)

    def l_forEach(self, expr, interpreter, operation):
        array = self.instance.array
        for element in array:
            operation.call(interpreter, expr, [element])

    def l_transform(self, expr, interpreter, mapping):
        array = self.instance.array
        newArray = []
        for element in array:
            value = mapping.call(interpreter, expr, [element])
            if type(value) == tuple:
                raise RuntimeError(expr.rightParen, "Function argument must return a value.")
            newArray.append(value)
        return List(newArray)

    def l_filter(self, expr, interpreter, condition):
        array = self.instance.array
        filterArray = []
        for element in array:
            predicate = condition.call(interpreter, expr, [element])
            if predicate == True:
                filterArray.append(element)
            elif predicate == False:
                pass
            else:
                raise RuntimeError(expr.rightParen, "Function argument must return a Boolean value.")
        return List(filterArray)

    def flatHelper(self, array):
        flatArray = []
        for element in array:
            if type(element) == List:
                flatArray += self.flatHelper(element.array)
            else:
                flatArray.append(element)
        return flatArray

    def l_flat(self, expr):
        array = self.instance.array
        return List(self.flatHelper(array))

    def l_contains(self, expr, element):
        for object in self.instance.array:
            if self.compareHelper(object, element):
                return True
        return False
    
    def l_duplicate(self, expr):
        array = self.instance.array
        return (len(array) != len(set(array)))

    def l_index(self, expr, element):
        for i, object in enumerate(self.instance.array):
            if self.compareHelper(object, element):
                return float(i)
        return #None

    def l_indexLast(self, expr, element):
        import copy
        array = copy.deepcopy(self.instance.array)
        array.reverse()
        for i, object in enumerate(array):
            if self.compareHelper(object, element):
                return float(len(array) - i - 1)
        return #None

    def l_any(self, expr, interpreter, condition):
        array = self.instance.array
        for element in array:
            predicate = condition.call(interpreter, expr, [element])
            if predicate == True:
                return True
            elif type(predicate) != bool:
                raise RuntimeError(expr.rightParen, "Function argument must return a Boolean value.")
        return False

    def l_all(self, expr, interpreter, condition):
        array = self.instance.array
        for element in array:
            predicate = condition.call(interpreter, expr, [element])
            if predicate == False:
                return False
            elif type(predicate) != bool:
                raise RuntimeError(expr.rightParen, "Function argument must return a Boolean value.")
        return True

    def l_reverse(self, expr):
        import copy
        array = copy.deepcopy(self.instance.array)
        array.reverse()
        return List(array)

    # Update to sort strings?
    def l_sort(self, expr, ascending: bool = True):
        import copy
        array = copy.deepcopy(self.instance.array)
        if (len(array) != 0) and (type(array[0]) == String):
            array = [obj.text for obj in array]
        array.sort(reverse = not ascending)
        if (len(array) != 0) and (type(array[0]) == str):
            array = [String(obj) for obj in array]
        return List(array)
    
    # Update comparisons for strings.
    def l_sorted(self, expr, ascending: bool = True):
        array = self.instance.array
        if (len(array) != 0) and (type(array[0]) == String):
            array = [obj.text for obj in array]
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
        # Already checked that each element in instance's array
        # is a list containing exactly two elements.
        array = self.instance.array
        largeList = [[], []]
        for element in array:
            elemArray = element.array
            largeList[0].append(elemArray[0])
            largeList[1].append(elemArray[1])
        return List(largeList)

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

    def check_add(self, expr, arguments):
        return True
    
    def check_insert(self, expr, arguments):
        return True
    
    def check_pop(self, expr, arguments):
        return True
    
    def check_remove(self, expr, arguments):
        index = arguments[0]
        if type(index) != float:
            raise RuntimeError(expr.rightParen, "Index argument must evaluate to a number.")
        if index < 0:
            raise RuntimeError(expr.rightParen, "Index value cannot be negative.")
        elif index >= len(self.instance.array):
            raise RuntimeError(expr.rightParen, "Index value is beyond list end.")
        return True
    
    def check_delete(self, expr, arguments):
        return True
    
    def check_join(self, expr, arguments):
        for obj in self.instance.array:
            if type(obj) != String:
                raise RuntimeError(expr.rightParen, 
                                   "List given must only contain strings.")
        return True
    
    def check_unique(self, expr, arguments):
        return True
    
    def check_forEach(self, expr, arguments):
        operation = arguments[0]
        if not isinstance(operation, LoxCallable):
            raise RuntimeError(expr.rightParen,
                               "Operation given is not a callable object.")
        return True
    
    def check_transform(self, expr, arguments):
        mapping = arguments[0]
        if not isinstance(mapping, LoxCallable):
            raise RuntimeError(expr.rightParen,
                               "Mapping given is not a callable object.")
        return True
    
    def check_filter(self, expr, arguments):
        condition = arguments[0]
        if not isinstance(condition, LoxCallable):
            raise RuntimeError(expr.rightParen,
                               "Filter given is not a callable object.")
        return True
    
    def check_flat(self, expr, arguments):
        return True
    
    def check_contains(self, expr, arguments):
        return True

    def check_duplicate(self, expr, arguments):
        return True
    
    def check_index(self, expr, arguments):
        return True
    
    def check_indexLast(self, expr, arguments):
        return True
    
    def check_any(self, expr, arguments):
        condition = arguments[0]
        if not isinstance(condition, LoxCallable):
            raise RuntimeError(expr.rightParen,
                               "Condition given is not a callable object.")
        return True
    
    def check_all(self, expr, arguments):
        condition = arguments[0]
        if not isinstance(condition, LoxCallable):
            raise RuntimeError(expr.rightParen,
                               "Condition given is not a callable object.")
        return True
    
    def check_reverse(self, expr, arguments):
        return True
    
    def check_sort(self, expr, arguments):
        array = self.instance.array
        if len(array) == 0:
            if (len(arguments) == 0) or (type(arguments[0]) == bool):
                return True
            else:
                raise RuntimeError(expr.rightParen,
                                   "Argument must be evaluate to a Boolean.")
        objType = type(array[0])
        if (objType != float) and (objType != String):
            raise RuntimeError(expr.rightParen,
                               "Elements can only be numbers or strings.")
        for i in range(1, len(array)):
            if type(array[i]) != objType:
                raise RuntimeError(expr.rightParen,
                                   "Cannot sort elements of different types.")
        if (len(arguments) == 0) or (type(arguments[0]) == bool):
            return True
        else:
            raise RuntimeError(expr.rightParen,
                                "Argument must evaluate to a Boolean.")

    def check_sorted(self, expr, arguments):
        array = self.instance.array
        if len(array) == 0:
            if (len(arguments) == 0) or (type(arguments[0]) == bool):
                return True
            else:
                raise RuntimeError(expr.rightParen,
                                   "Argument must be evaluate to a Boolean.")
        objType = type(array[0])
        if (objType != float) and (objType != String):
            raise RuntimeError(expr.rightParen,
                               "Elements can only be numbers or strings.")
        for i in range(1, len(array)):
            if type(array[i]) != objType:
                raise RuntimeError(expr.rightParen,
                                   "Cannot compare elements of different types.")
        if (len(arguments) == 0) or (type(arguments[0]) == bool):
            return True
        else:
            raise RuntimeError(expr.rightParen,
                                "Argument must evaluate to a Boolean.")
    
    def check_pair(self, expr, arguments):
        if type(arguments[0]) != List:
            raise RuntimeError(expr.rightParen,
                               "Argument must be a list.")
        return True
    
    def check_separate(self, expr, arguments):
        array = self.instance.array
        if len(array) == 0:
            return True
        for x in array:
            if type(x) != List:
                raise RuntimeError(expr.rightParen,
                                   "Elements must be lists.")
            elif len(x.array) != 2:
                raise RuntimeError(expr.rightParen,
                                   "Elements must be lists containing exactly two elements.")
        return True
    
    def check_sum(self, expr, arguments):
        array = self.instance.array
        if len(array) == 0:
            return True
        for x in array:
            if type(x) != float:
                raise RuntimeError(expr.rightParen,
                                   "List must contain numbers only.")
        return True
    
    def check_min(self, expr, arguments):
        array = self.instance.array
        if len(array) == 0:
            return True
        for x in array:
            if type(x) != float:
                raise RuntimeError(expr.rightParen,
                                   "List must contain numbers only.")
        return True
    
    def check_max(self, expr, arguments):
        array = self.instance.array
        if len(array) == 0:
            return True
        for x in array:
            if type(x) != float:
                raise RuntimeError(expr.rightParen,
                                   "List must contain numbers only.")
        return True

    def check_average(self, expr, arguments):
        array = self.instance.array
        if len(array) == 0:
            return True
        for x in array:
            if type(x) != float:
                raise RuntimeError(expr.rightParen,
                                   "List must contain numbers only.")
        return True

    # ------------------------------------------------------------

    def arity(self):
        match self.mode:
            case "add":
                return [1,1]
            case "insert":
                return [2,2]
            case "pop":
                return [0,0]
            case "remove":
                return [1,1]
            case "delete":
                return [1,2]

            case "join":
                return [0,0]
            case "unique":
                return [0,0]
            case "forEach":
                return [1,1]
            case "transform":
                return [1,1]
            case "filter":
                return [1,1]
            case "flat":
                return [0,0]

            case "contains":
                return [1,1]
            case "duplicate":
                return [0,0]
            case "index":
                return [1,1]
            case "indexLast":
                return [1,1]
            case "any":
                return [1,1]
            case "all":
                return [1,1]

            case "reverse":
                return [0,0]
            case "sort":
                return [0,1]
            case "sorted":
                return [0,1]
            case "pair":
                return [1,1]
            case "separate":
                return [0,0]

            case "sum":
                return [0,0]
            case "min":
                return [0,0]
            case "max":
                return [0,0]
            case "average":
                return [0,0]
    
    # ------------------------------------------------------------
    def toString(self):
        return "<list method>"

functions = ["add", "insert", "pop", "remove", "delete",
             "join", "unique", "forEach", "transform", "filter", "flat",
             "contains", "duplicate", "index", "indexLast", "any", "all", "collect",
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
            if type(element) == String:
                string += "\""
            string += dummyInterpreter.stringify(element)
            if type(element) == String:
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
    
    def check(self, expr, arguments):
        if len(arguments) == 0:
            return True
        obj = arguments[0]
        argType = type(obj)
        if (argType == List) or (argType == String):
            return True
        elif argType == float:
            if int(obj) == obj:
                return True
        raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: list/string/integer.")

    def call(self, interpreter, expr, arguments):
        if self.check(expr, arguments):
            if len(arguments) > 0:
                obj = arguments[0]
                if type(obj) == List:
                    return List(obj.array)
                elif type(obj) == String:
                    array = list()
                    string = obj.text
                    for char in string:
                        array.append(String(char))
                    return List(array)
                elif type(obj) == float:
                    length = int(obj)
                    array = list()
                    for i in range(0, length):
                        array.append(None)
                    return List(array)
            else:
                return List([])

    def arity(self):
        return [0,1]
    
    def toString(self):
        return "<List constructor>"

initList = ListInit()