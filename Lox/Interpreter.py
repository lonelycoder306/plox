from Token import Token, TokenType
from Expr import Expr
from Stmt import Stmt
from Environment import Environment
from LoxCallable import LoxCallable
from LoxFunction import LoxFunction
from LoxClass import LoxClass
from LoxInstance import LoxInstance, InstanceFunction
from LoxGroup import LoxGroup
from List import List, initList
from BuiltinFunction import BuiltinFunction
from Error import RuntimeError, BreakError, ContinueError, Return, StopError, UserError
from Warning import UserWarning
from Debug import CLISwitch
from String import String
from Reference import Reference

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.loopLevel = 0
        self.locals = dict()
        self.ExprStmt = False

        # Setting up built-in functions in global scope.
        from BuiltinFunction import builtinSetUp
        builtinSetUp()
        from BuiltinFunction import builtins
        # Setting up the List() constructor.
        builtins.define("List", initList, "VAR")
        self.builtins = builtins

    def interpret(self, statements):
        try:
            for statement in statements:
                try:
                    self.execute(statement)
                except UserError as error:
                    error.show(self)
                    if error.error.private["halt"] == True:
                        return
                except UserWarning as warning:
                    warning.show(self)
        except RecursionError:
            import sys
            sys.stderr.write("Recursion error: Recursion limit exceeded.\n")
            return
        except RuntimeError as error: # Stops all execution.
            error.show()
        except StopError:
            return
        except CLISwitch:
            import State
            State.switchCLI = True
            return
    
    def resolve(self, expr: Expr.Variable, depth: int):
        self.locals[expr] = depth
    
    def execute(self, stmt):
        return stmt.accept(self)
    
    def executeBlock(self, statements, environment: Environment):
        previous = self.environment
        import State
        currentCallStack = State.callStack
        try:
            self.environment = environment
            import copy
            State.callStack = copy.deepcopy(State.callStack)

            for statement in statements:
                try:
                    self.execute(statement)
                except UserWarning as warning:
                    warning.show(self)
        finally:
            self.environment = previous
            State.callStack = currentCallStack

    # No need to check that 'break' or 'continue' are inside a loop, since their presence outside one 
    # raises a Parse Error (before the interpreter phase).
    # Making it a Parse Error rather than a Runtime Error avoids the case where 'break' and 'continue' are
    # placed inside the block after a false condition; 
    # the program will never run those statements, so no error gets raised (despite it being bad code).
    def visitBreakStmt(self, stmt: Stmt.Break):
        raise BreakError(stmt.breakCMD, stmt.loopType)

    def visitBlockStmt(self, stmt: Stmt.Block):
        self.executeBlock(stmt.statements, Environment(self.environment))
    
    def methodSetUp(self, methodDict: list):
        newDict = {}
        for method in methodDict:
            variadic = False
            if (method.params != None) and len(method.params) != 0:
                if ((type(method.params[-1]) == Token) and
                    (method.params[-1].type == TokenType.ELLIPSIS)):
                    variadic = True
            context = {"isMethod": True, 
                       "isInitializer": False, 
                       "class": None, # Temporarily.
                       "safe": False,
                       "variadic": variadic}
            function = LoxFunction(method, self.environment, context)
            newDict[method.name.lexeme] = function
        return newDict

    def visitClassStmt(self, stmt: Stmt.Class):
        self.environment.define(stmt.name.lexeme, None, "VAR")

        superclass = None
        if stmt.superclass != None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(stmt.superclass.name, 
                            "Superclass must be a class.")
        
        if stmt.superclass != None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass, "VAR")

        classMethods = self.methodSetUp(stmt.classMethods)
        
        metaclass = LoxClass(None, superclass, f"{stmt.name.lexeme} metaclass", {}, classMethods)
        for method in metaclass.public.values():
            method.context["class"] = metaclass

        private = self.methodSetUp(stmt.private)
        public = self.methodSetUp(stmt.public)

        klass = LoxClass(metaclass, superclass, stmt.name.lexeme, private, public)
        for method in klass.private.values():
            method.context["class"] = klass
        for method in klass.public.values():
            method.context["class"] = klass
        
        public["_fieldList"] = InstanceFunction("_fieldList")
        public["_methodList"] = InstanceFunction("_methodList")
        public["_fields"] = InstanceFunction("_fields")
        public["_methods"] = InstanceFunction("_methods")

        if stmt.superclass != None:
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, klass)

    def visitContinueStmt(self, stmt: Stmt.Continue):
        raise ContinueError(stmt.continueCMD, stmt.loopType)

    def visitErrorStmt(self, stmt: Stmt.Error):
        errors = []
        if stmt.errors != None:
            for error in stmt.errors:
                errors.append(error.name.lexeme)
            try:
                self.execute(stmt.body)
            except UserError as e:
                if e.error.klass.name in errors:
                    self.execute(stmt.handler)
                else:
                    raise
            except UserWarning as w:
                if w.warning.klass.name in errors:
                    self.execute(stmt.handler)
                else:
                    raise
            except RuntimeError:
                if "RuntimeError" in errors:
                    self.execute(stmt.handler)
                else:
                    raise
            except RecursionError:
                if "RecursionError" in errors:
                    self.execute(stmt.handler)
                else:
                    raise

        else:
            try:
                self.execute(stmt.body)
            except (UserError, UserWarning, RuntimeError, RecursionError):
                self.execute(stmt.handler)

    def visitExpressionStmt(self, stmt: Stmt.Expression):
        prevState = self.ExprStmt
        self.ExprStmt = True

        # Print out the return value of any expression statement.
        # Assignments/field assignments are excluded so that the RHS of an assignment 
        # is not automatically printed every time an assignment is carried out.
        # Have chosen not to exclude comma expressions. Thus, the value of the 
        # last expression is printed to the screen.
        types = (Expr.Assign, Expr.Set, Expr.Modify)
        if type(stmt.expression) not in types:
            self.visitPrintStmt(Stmt.Print(stmt.expression))
        
        else:
            self.evaluate(stmt.expression)
        
        self.ExprStmt = prevState
    
    def visitFetchStmt(self, stmt: Stmt.Fetch):
        mode = stmt.mode.lexeme[3:]
        name = stmt.name.lexeme[1:-1]
        match mode:
            case "Mod":
                try:
                    import os
                    import sys
                    from importlib import import_module
                    sys.path.append(os.getcwd() + "/Modules")
                    module = import_module(f"{name}")
                    setUp = getattr(module, f"{name}SetUp")
                    setUp()
                    env = getattr(module, name)
                    self.environment.values.update(env.values)
                    sys.path.pop()
                except ModuleNotFoundError:
                    raise RuntimeError(stmt.name, "Module not found.")
            case "Lib":
                pass
            case "File":
                pass

    def visitFunctionStmt(self, stmt: Stmt.Function):
        # Check that function is not an unassigned lambda (do nothing if it is).
        if stmt.name != None:
            context = {"isMethod": False,
                       "isInitializer": False,
                       "class": None,
                       "safe": False}
            if len(stmt.params) == 0:
                context["variadic"] = False
            else:
                param = stmt.params[-1]
                if (type(param) == Token) and (param.type == TokenType.ELLIPSIS):
                    context["variadic"] = True
                else:
                    context["variadic"] = False
            function = LoxFunction(stmt, self.environment, context)
            self.environment.define(stmt.name.lexeme, function, "VAR")
    
    def visitGroupStmt(self, stmt: Stmt.Group):
        newEnv = Environment(self.environment)
        previous = self.environment
        self.environment = newEnv
        for var in stmt.vars:
            self.execute(var)
        for func in stmt.functions:
            self.execute(func)
        for klass in stmt.classes:
            self.execute(klass)
        group = LoxGroup(stmt.name.lexeme, newEnv)
        self.environment = previous
        self.environment.define(stmt.name.lexeme, group, "VAR")

    def visitIfStmt(self, stmt: Stmt.If):
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch != None:
            self.execute(stmt.elseBranch)

    def visitListStmt(self, stmt: Stmt.List):
        # We could make uninitialized lists remain undefined,
        # but it seems more fitting to simply initialize them by default
        # to an empty list, particularly since list variables cannot
        # possibly hold values of any type but list (or List, technically).
        listInstance = List([])
        if stmt.initializer != None:
            listInstance = self.evaluate(stmt.initializer)
            if type(listInstance) == Reference:
                listInstance = listInstance.object
            else:
                import copy
                listInstance = copy.deepcopy(listInstance)
            if type(listInstance) != List:
                raise RuntimeError(stmt.name, "Cannot initialize list with non-list value.")
        self.environment.define(stmt.name.lexeme, listInstance, "VAR")

    def visitPrintStmt(self, stmt: Stmt.Print):
        value = self.evaluate(stmt.expression)
        # Prevent method from printing nil for void functions when they are called in an expression statement.
        # No return value -> implicitly return None -> prints "nil".
        if (self.ExprStmt) and (type(value) == tuple):
            return
        print(self.stringify(value))

    def exceptClassHelper(self, klass: LoxClass):
        if klass.name == "Error":
            return (True, "Error")
        elif klass.name == "Warning":
            return (True, "Warning")
        else:
            while klass.superclass != None:
                klass = klass.superclass
                if klass.name == "Error":
                    return (True, "Error")
                elif klass.name == "Warning":
                    return (True, "Warning")
            return (False, None)

    def visitReportStmt(self, stmt: Stmt.Report):
        exception = self.evaluate(stmt.exception)
        if type(exception) != LoxInstance:
            raise RuntimeError(stmt.keyword, 
                               "Cannot report an exception on non-exception object.")
        check = self.exceptClassHelper(exception.klass)
        if not check[0]:
            raise RuntimeError(stmt.keyword, 
                               "Cannot report an exception on non-exception object.")
        if check[1] == "Error":
            raise UserError(exception, stmt.exception)
        elif check[1] == "Warning":
            raise UserWarning(exception, stmt.exception)

    def visitReturnStmt(self, stmt: Stmt.Return):
        value = ()
        if stmt.value != None:
            value = self.evaluate(stmt.value)
        
        raise Return(value)

    def visitVarStmt(self, stmt: Stmt.Var):
        # Default value will be a tuple containing only None.
        # Reasoning: Since Lox does not support tuples, a user cannot assign this value to a variable (whether intentionally or otherwise).
        # Thus, if this is the value of a variable we are checking, then the variable must be uninitialized in the user's code.
        # Chose to make it a tuple instead of a list since lists may be implemented later (unlikely for tuples).
        value = tuple()
        if stmt.initializer != None:
            value = self.evaluate(stmt.initializer)
        
        if type(value) == Reference:
            value = value.object

        elif type(value) == String:
            import copy
            value = copy.deepcopy(value)

        if type(value) == List:
            raise RuntimeError(stmt.equals, "Cannot assign list to variable with 'var' modifier.")

        self.environment.define(stmt.name.lexeme, value, stmt.access)

    def visitWhileStmt(self, stmt: Stmt.While):
        self.loopLevel += 1
        while self.isTruthy(self.evaluate(stmt.condition)):
            try:
                self.execute(stmt.body)
            except BreakError:
                break
            except ContinueError as error:
                if error.loopType == "whileLoop":
                    pass
                # Evaluate the increment expression if loop is a for-loop.
                elif error.loopType == "forLoop":
                    self.evaluate(stmt.body.statements[-1])
        self.loopLevel -= 1
    
    def checkNumberOperand(self, operator, operand):
        if type(operand) == float:
            return
        
        raise RuntimeError(operator, "Operand must be a number.")
    
    def checkNumberOperands(self, operator, left, right):
        if (type(left) == float) and (type(right) == float):
            return
        
        raise RuntimeError(operator, "Operands must be numbers.")
    
    def varType(self, object):
        # To check if variable holds a datetime.time 
        # object (return value of clock()).
        from datetime import time
        match object:
            case float(): # No check for int() since all values in Lox are saved as floats/doubles.
                return "number"
            case String():
                return "string"
            case bool(): # Fun fact: Bool is a subclass of int.
                return "boolean"
            case bytes():
                return "bytes"
            case List():
                return "list"
            case Reference():
                return self.varType(object.object) + " reference"
            case LoxFunction():
                if object.declaration.name == None:
                    return "lambda"
                else:
                    return "function"
            case BuiltinFunction():
                return "native function"
            case InstanceFunction():
                return "native method"
            case _ if isinstance(object, LoxCallable):
                return object.toString()[1:-1]
            case _ if isinstance(object, time): # Format to check Boolean conditions in match-case structure.
                return "datetime"
            case _ if isinstance(object, LoxClass):
                return "class"
            case _ if isinstance(object, LoxInstance):
                return object.varType()
            case _:
                return "unknown type"
    
    def isTruthy(self, object) -> bool:
        if object == None:
            return False
        
        if type(object) == bool:
            return object
        
        return True
    
    def stringify(self, object) -> str:
        if object == None:
            return "nil"
        
        if isinstance(object, LoxCallable):
            return object.toString()
        if type(object) == LoxInstance:
            return object.toString(self)
        if type(object) == LoxGroup:
            return object.toString()
        if type(object) == list:
            return str(List(object))
        if type(object) == Reference:
            return "<" + self.varType(object) + ">"
        
        # Booleans in Lox are all-lowercase, unlike in Python.
        if type(object) == bool:
            if object == True:
                return "true"
            else:
                return "false"
        
        # The built-in Python print() function can print objects of almost any data-type,
        # so we only interfere with it if we wish to have some particular formatted output.
        text = str(object)

        if type(object) == float:
            if text[-2:] == ".0":
                text = text[:-2]

        return text
    
    def lookUpVariable(self, name: Token, expr: Expr):
        import State as State
        if State.debugMode:
            if name.lexeme in self.builtins.values.keys():
                return self.builtins.get(name)
            # Global user-defined functions can't be called,
            # since they could themselves contain breakpoints,
            # leading to very messy debugger problems.
            return self.environment.get(name)

        distance = self.locals.get(expr, None)
        if distance != None:
            value = self.environment.getAt(distance, name)
            return value
        else:
            if name.lexeme in self.globals.values.keys():
                return self.globals.get(name)
            elif name.lexeme in self.builtins.values.keys():
                return self.builtins.get(name)
            return self.environment.get(name)
    
    def checkIndices(self, expr, object, start, end):
        length = len(object)
        # Start index is too negative (goes beyond the beginning).
        if start < (-1*length):
            raise RuntimeError(expr.operator, "Start index out of bounds.")
        # Single index is too high (goes beyond the end).
        elif (end == None) and (start >= length):
            raise RuntimeError(expr.operator, "Index out of bounds.")
        # Start index is negative despite there being another index, i.e.,
        # accessing a part of a list/string.
        elif (end != None) and (start < 0):
            raise RuntimeError(expr.operator, "Start index out of bounds.")
        elif end != None:
            # If end is positive, it cannot be larger than the start.
            # If it is negative, it cannot go backwards beyond the beginning.
            if ((end > 0) and (end < start)) or (end < (-1*length)):
                raise RuntimeError(expr.operator, "End index out of bounds.")
        return True
    
    def accessElements(self, object, start, end, expr: Expr.Access):
        if (type(start) != float) or (int(start) != start):
            raise RuntimeError(expr.operator, "Start index must be an integer.")
        
        if end != None:
            if (type(end) != float) or (int(end) != end):
                raise RuntimeError(expr.operator, "End index must be an integer.")

        if type(object) == String:
            object = object.text
            length = len(object)
        elif type(object) == List:
            object = object.array
            length = len(object)
        if self.checkIndices(expr, object, start, end):
            if end == None: # Only accessing a single element.
                return object[int(start)]
            else: # Possibly accessing a range.
                return object[int(start) : int(end) + 1]
    
    def plus(self, expr, left, right):
        if (type(left) == list) and (type(right) == list):
            return List(left + right)

        if (type(left) == float) and (type(right) == float):
            return (float(left) + float(right))
        
        if (type(left) == str) and (type(right) == str):
            return String(str(left) + str(right))
        
        # Allows for concatenation of a string and a non-numeric variable as well.
        if type(left) == str:
            return String(str(left) + self.stringify(right))
        
        if type(right) == str:
            return String(self.stringify(left) + str(right))
        
        raise RuntimeError(expr.operator, "Cannot add given operands.")
    
    def star(self, expr, left, right):
        if type(left) == str:
            if type(right) == float:
                if int(right) == right:
                    return String(left * int(right))
                raise RuntimeError(expr.operator, 
                                    "Cannot multiply string by non-integer number.")
            elif type(right) == str:
                raise RuntimeError(expr.operator, 
                                    "Cannot multiply string by string.")
            
            elif type(right) == bool:
                return left * right
        
        elif type(right) == str:
            if type(left) == float:
                if int(left) == left:
                    return String(right * int(left))
                raise RuntimeError(expr.operator, 
                                    "Cannot multiply string by non-integer number.")
            elif type(left) == str:
                raise RuntimeError(expr.operator, 
                                    "Cannot multiply string by string.")

            elif type(left) == bool:
                return left * right

        options = [(float, float), (float, bool), (bool, float), (bool, bool)]
        if (type(left), type(right)) in options:
            return (float(left) * float(right))
        
        raise RuntimeError(expr.operator, "Invalid product.")
    
    def manageStack(self, expr, callee):
        import State as State
        token = None
        if type(expr.callee) == Expr.Variable:
            token = expr.callee.name
        # Function object is being accessed from a list
        # or as a field.
        elif (type(expr) == Expr.Get) or (type(expr) == Expr.Access):
            # LoxFunction object (and not a lambda).
            if ((type(callee) == LoxFunction) 
                and (callee.declaration.name != None)):
                token = callee.declaration.name
        funcData = {}
        if token != None:
            funcData = {"name": token.lexeme,
                        "file": token.fileName,
                        "line": token.line}
        else:
            # Closest token we can get.
            token = expr.leftParen
            name = "lambda"
            # Function is another type of function object
            # (not even a lambda).
            if type(callee) != LoxFunction:
                name = callee.mode
            funcData = {"name": name,
                        "file": token.fileName,
                        "line": token.line}
        State.callStack.insert(0, funcData)
        State.traceLog.insert(0, funcData)
    
    def modifyString(self, mod, value, expr):
        start = self.evaluate(expr.part.start)
        end = None
        if expr.part.end != None:
            end = self.evaluate(expr.part.end)

        # Error check.
        if type(value) != String:
            raise RuntimeError(expr.operator, "Can only assign string to string part.")

        # Strings in Python are immutable.
        # They, thus, do not support direct item assignment.
        # Thus, we turn the string into a list of its characters,
        # make our modifications, and put it back together.

        string = mod.text
        if self.checkIndices(expr, string, start, end):
            tempList = list(string)
            if end == None:
                tempList[int(start)] = value.text
            else:
                tempList[int(start) : int(end) + 1] = value.text
            string = "".join(tempList)
        mod.text = string
    
    def modifyList(self, mod, value, expr):
        start = self.evaluate(expr.part.start)
        end = None
        if expr.part.end != None:
            end = self.evaluate(expr.part.end)

        # Any value can be assigned to an *element* of a list,
        # so no type-check needed here.
        if self.checkIndices(expr, mod.array, start, end):
            if end == None:
                mod.array[int(start)] = value
            else:
                # Error check.
                if type(value) != List:
                    raise RuntimeError(expr.operator, "Can only assign list to list part.")
                # We cannot modify an actual (built-in) list object with a custom List object.
                # We thus turn value into its built-in list field.
                value = value.array
                mod.array[int(start) : int(end) + 1] = value
    
    def evaluate(self, expr):
        return expr.accept(self)
    
    def visitAccessExpr(self, expr: Expr.Access):
        object = self.evaluate(expr.object)
        start = self.evaluate(expr.start)
        end = None
        if expr.end != None:
            end = self.evaluate(expr.end)
        
        if type(object) == String:
            output = self.accessElements(object, start, end, expr)
            if type(output) == str:
                return String(output)
            elif type(output) == list:
                return List(output)
            return output
        elif type(object) == List:
            output = self.accessElements(object, start, end, expr)
            if type(output) == list:
                return List(output)
            return output
        else:
            raise RuntimeError(expr.operator, "Member access only for strings and lists.")

    def visitAssignExpr(self, expr: Expr.Assign):
        value = self.evaluate(expr.value)
        if type(value) == Reference:
            value = value.object
        elif (type(value) == List) or (type(value) == String):
            import copy
            value = copy.deepcopy(value)

        distance = self.locals.get(expr, None)
        if distance != None:
            self.environment.assignAt(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visitBinaryExpr(self, expr: Expr.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        if type(left) == List:
            left = left.array
        elif type(left) == String:
            left = left.text
        if type(right) == List:
            right = right.array
        elif type(right) == String:
            right = right.text

        match expr.operator.type:
            case TokenType.GREATER:
                if ((type(left) == type(right) == float) or 
                (type(left) == type(right) == str)):
                    return (left > right)
                raise RuntimeError(expr.operator, "Operands must be strings or numbers.")
            case TokenType.GREATER_EQUAL:
                if ((type(left) == type(right) == float) or 
                (type(left) == type(right) == str)):
                    return (left >= right)
                raise RuntimeError(expr.operator, "Operands must be strings or numbers.")
            case TokenType.LESS:
                if ((type(left) == type(right) == float) or 
                (type(left) == type(right) == str)):
                    return (left < right)
                raise RuntimeError(expr.operator, "Operands must be strings or numbers.")
            case TokenType.LESS_EQUAL:
                if ((type(left) == type(right) == float) or 
                (type(left) == type(right) == str)):
                    return (left <= right)
                raise RuntimeError(expr.operator, "Operands must be strings or numbers.")
            case TokenType.BANG_EQUAL:
                return (type(left) != type(right) or (left != right))
            case TokenType.EQUAL_EQUAL:
                return (type(left) == type(right) and (left == right))
            case TokenType.MINUS:
                self.checkNumberOperands(expr.operator, left, right)
                return (float(left) - float(right))
            case TokenType.PLUS:
                return self.plus(expr, left, right)
            case TokenType.SLASH:
                self.checkNumberOperands(expr.operator, left, right)
                # Comparison with 0 works even for floats.
                if float(right) == 0:
                    raise RuntimeError(expr.operator, "Division by zero not allowed.")
                return (float(left) / float(right))
            case TokenType.STAR:
                return self.star(expr, left, right)
            case TokenType.MOD:
                self.checkNumberOperands(expr.operator, left, right)
                if float(right) == 0:
                    raise RuntimeError(expr.operator, "Cannot compute value mod 0.")
                return (float(left) % float(right))
            case TokenType.POWER:
                self.checkNumberOperands(expr.operator, left, right)
                # Note: Python evaluates 0^0 as 1.
                return (float(left) ** float(right))

    def visitCallExpr(self, expr: Expr.Call):
        callee = self.evaluate(expr.callee)

        arguments = list()
        for argument in expr.arguments:
            value = self.evaluate(argument)
            if (type(value) == List) or (type(value) == String):
                if (type(callee) != BuiltinFunction) or (callee.mode != "reference"):
                    import copy
                    value = copy.deepcopy(value)
            if type(value) == Reference:
                if (type(callee) != BuiltinFunction) or (callee.mode != "type"):
                    value = value.object
            arguments.append(value)
        
        if not isinstance(callee, LoxCallable):
            raise RuntimeError(expr.leftParen, "No such function or class.")

        self.manageStack(expr, callee)
        
        arity = callee.arity()
        if (len(arguments) < arity[0]):
            if arity[0] == 1: # To make argument singular rather than plural (plural for 0 as well).
                raise RuntimeError(expr.rightParen, 
                               f"Expected minimum {arity[0]} argument but got {len(arguments)}.")
            else:
                raise RuntimeError(expr.rightParen, 
                               f"Expected minimum {arity[0]} arguments but got {len(arguments)}.")
        if len(arguments) > arity[1]:
            if arity[1] == 1:
                raise RuntimeError(expr.rightParen, 
                               f"Expected maximum {arity[1]} argument but got {len(arguments)}.")
            else:
                raise RuntimeError(expr.rightParen, 
                               f"Expected maximum {arity[1]} arguments but got {len(arguments)}.")
        
        return callee.call(self, expr, arguments)

    def visitCommaExpr(self, expr: Expr.Comma):
        expressions = expr.expressions
        expressionNumber = len(expressions)
        for i in range(0, expressionNumber - 1):
            self.evaluate(expressions[i])
        
        return self.evaluate(expressions[-1])
    
    def visitGetExpr(self, expr: Expr.Get):
        object = self.evaluate(expr.object)
        if (isinstance(object, LoxInstance)) or (type(object) == List):
            result = object.get(expr.name)
            if isinstance(result, LoxFunction) and result.isGetter():
                result = result.call(self, None, None)
            
            return result
        
        raise RuntimeError(expr.name, "Only instances have properties.")

    def visitGroupingExpr(self, expr: Expr.Grouping):
        return self.evaluate(expr.expression)

    # Lambdas can all be given default name None since they are accessed by index in the parameter/argument list, not by name.
    def visitLambdaExpr(self, expr: Expr.Lambda):
        lambdaDeclaration = Stmt.Function(None, expr.params, expr.body, expr.defaults)
        context = {"isMethod": False,
                   "isInitializer": False,
                   "class": None,
                   "safe": False}
        if len(expr.params) == 0:
            context["variadic"] = False
        else:
            param = expr.params[-1]
            if (type(param) == Token) and (param.type == TokenType.ELLIPSIS):
                context["variadic"] = True
            else:
                context["variadic"] = False
        return LoxFunction(lambdaDeclaration, self.environment, context)

    def visitLiteralExpr(self, expr: Expr.Literal):
        return expr.value
    
    def visitListExpr(self, expr: Expr.List):
        elements = []
        for element in expr.elements:
            value = self.evaluate(element)
            if type(value) == Reference:
                value = value.object
            elements.append(value)
        return List(elements)
    
    def visitLogicalExpr(self, expr: Expr.Logical):
        left = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.isTruthy(left):
                return left
        else:
            if not self.isTruthy(left):
                return left
        
        return self.evaluate(expr.right)
    
    def visitModifyExpr(self, expr: Expr.Modify):
        value = self.evaluate(expr.value)

        validObjTypes = (Expr.Variable, Expr.Get, Expr.Access)
        objType = type(expr.part.object)
        if objType not in validObjTypes:
            raise RuntimeError(expr.operator, "Left-hand value not modifiable.")
        mod = self.evaluate(expr.part.object)
        if (type(mod) != String) and (type(mod) != List):
            raise RuntimeError(expr.operator, "Left-hand value not modifiable.")

        if type(mod) == String:
            self.modifyString(mod, value, expr)

        elif type(mod) == List:
            self.modifyList(mod, value, expr)
        return value
    
    def visitSetExpr(self, expr: Expr.Set):
        object = self.evaluate(expr.object)

        if (isinstance(object, LoxInstance)):
            value = self.evaluate(expr.value)
            if type(value) == List:
                import copy
                value = copy.deepcopy(value)
            object.set(expr.name, value, expr.access)
            return value
        
        raise RuntimeError(expr.name, "Only instances have modifiable fields.")

    def visitSuperExpr(self, expr: Expr.Super):
        distance = self.locals.get(expr, None)
        dummySuper = Token(TokenType.SUPER, "super", "super",
                           0, 0, None)
        dummyThis = Token(TokenType.THIS, "this", "this",
                          0, 0, None)
        superclass = self.environment.getAt(distance, dummySuper)
        object = self.environment.getAt(distance - 1, dummyThis)
        method = superclass.findMethod(expr.method.lexeme, expr.method)

        if method == None:
            raise RuntimeError(expr.method, 
                               f"Undefined property '{expr.method.lexeme}'.")

        return method.bind(object)
    
    # Ternary implementation my own.
    def visitTernaryExpr(self, expr: Expr.Ternary):
        if self.isTruthy(self.evaluate(expr.condition)):
            return self.evaluate(expr.trueBranch)
        return self.evaluate(expr.falseBranch)
    
    def visitThisExpr(self, expr: Expr.This):
        return self.lookUpVariable(expr.keyword, expr)

    def visitUnaryExpr(self, expr: Expr.Unary):
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.BANG:
                return not self.isTruthy(right)
            case TokenType.MINUS:
                self.checkNumberOperand(expr.operator, right)
                return -1 * float(right)

    def visitVariableExpr(self, expr: Expr.Variable):
        return self.lookUpVariable(expr.name, expr)