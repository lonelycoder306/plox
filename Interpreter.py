from Token import Token, TokenType
from Expr import Expr
from Stmt import Stmt
from Environment import Environment
from LoxCallable import LoxCallable
from LoxFunction import LoxFunction
from LoxClass import LoxClass
from LoxInstance import LoxInstance
from List import List, initList
from BuiltinFunction import BuiltinFunction
from Error import RuntimeError, breakError, continueError, Return
from Debug import breakpointStop

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        # varEnvs is a list of lists, each entry containing the environments currently in scope.
        # Allows us to have scoped imports, i.e., import a module but only within a particular scope.
        # Enter a scope -> Append a list with globals and builtins (they are defined in every scope).
        # Exit a scope -> Pop the last list from the varEnvs stack.
        # Function (variable) look-up is done over the last list in the varEnvs stack.
        # After popping, any imports in the scope no longer apply outside it.
        self.varEnvs = [[self.globals]] # List of all the environments we reference for variable/function names.
        self.loopLevel = 0
        self.locals = dict()

        # Setting up built-in functions in global scope.
        from BuiltinFunction import builtinSetUp
        builtinSetUp()
        from BuiltinFunction import builtins
        self.varEnvs[0].append(builtins)

        # Setting up the List() constructor.
        self.globals.define("List", initList)

    def interpret(self, statements):
        try:
            for statement in statements:
                try:
                    self.execute(statement)
                except breakpointStop as bp: # Only stops current line execution.
                    bp.debugStart() # Run first before checking switchCLI since it is only changed by the debugger.
                    import State
                    if State.switchCLI:
                        return
        except RuntimeError as error: # Stops all execution.
            error.show()
    
    def resolve(self, expr: Expr.Variable, depth: int):
        self.locals[expr] = depth
    
    def execute(self, stmt):
        return stmt.accept(self)
    
    def executeBlock(self, statements, environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            lastEnv = self.varEnvs[-1]
            # Copy everything in the last environment into the new environment.
            # Make a shallow copy so objects defined in the new environment
            # don't stay behind once the scope is exited.
            # Allows imports in an outer scope to still be defined in an inner scope.
            self.varEnvs.append(lastEnv.copy())

            for statement in statements:
                self.execute(statement)
        finally:
            self.varEnvs.pop()
            self.environment = previous

    # No need to check that 'break' or 'continue' are inside a loop, since their presence outside one 
    # raises a Parse Error (before the interpreter phase).
    # Making it a Parse Error rather than a Runtime Error avoids the case where 'break' and 'continue' are
    # placed inside the block after a false condition; 
    # the program will never run those statements, so no error gets raised (despite it being bad code).
    def visitBreakStmt(self, stmt: Stmt.Break):
        raise breakError(stmt.breakCMD, stmt.loopType)

    def visitBlockStmt(self, stmt: Stmt.Block):
        self.executeBlock(stmt.statements, Environment(self.environment))
    
    def visitClassStmt(self, stmt: Stmt.Class):
        self.environment.define(stmt.name.lexeme, None)

        methods = dict()
        for method in stmt.methods:
            function = LoxFunction(method, self.environment, 
                                   method.name.lexeme == "init")
            methods[method.name.lexeme] = function

        klass = LoxClass(stmt.name.lexeme, methods)
        self.environment.assign(stmt.name, klass)

    def visitContinueStmt(self, stmt: Stmt.Continue):
        raise continueError(stmt.continueCMD, stmt.loopType)

    def visitExpressionStmt(self, stmt: Stmt.Expression):
        # Print out the return value of any expression statement 
        # (except assignments, function calls, and comma-combined expressions).
        # Assignments/field assignments are excluded so that the RHS of an assignment 
        # is not automatically printed every time an assignment is carried out.
        # Have chosen not to exclude comma expressions. Thus, the value of the 
        # last expression is printed to the screen.
        types = (Expr.Assign, Expr.Set, Expr.Modify)
        if type(stmt.expression) not in types:
            self.visitPrintStmt(Stmt.Print(stmt.expression))
        
        else:
            self.evaluate(stmt.expression)
    
    def visitFetchStmt(self, stmt: Stmt.Fetch):
        import importlib
        mode = stmt.mode.lexeme[3:]
        name = stmt.name.lexeme[1:-1]
        match mode:
            case "Mod":
                try:
                    module = importlib.import_module(f"Modules.{name}")
                    setUp = getattr(module, f"{name}SetUp")
                    setUp()
                    env = getattr(module, name)
                    self.varEnvs[-1].append(env)
                except ModuleNotFoundError:
                    raise RuntimeError(stmt.name, "Module not found.")
            case "Lib":
                pass
            case "File":
                pass

    def visitFunctionStmt(self, stmt: Stmt.Function):
        # Check that function is not an unassigned lambda (do nothing if it is).
        if stmt.name != None:
            function = LoxFunction(stmt, self.environment, False)
            self.environment.define(stmt.name.lexeme, function)

    def visitIfStmt(self, stmt: Stmt.If):
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch != None:
            self.execute(stmt.elseBranch)

    def visitListStmt(self, stmt: Stmt.List):
        listInstance = None
        if stmt.initializer != None:
            listInstance = self.evaluate(stmt.initializer)
            if type(listInstance) != List:
                raise RuntimeError(stmt.name, "Cannot initialize list to non-list value.")
        self.environment.define(stmt.name.lexeme, listInstance)

    def visitPrintStmt(self, stmt: Stmt.Print):
        value = self.evaluate(stmt.expression)
        # Prevent method from printing nil for void functions when they are called in an expression statement.
        # No return value -> implicitly return None -> prints "nil".
        if (type(stmt.expression) == Expr.Call) and (value == None):
            return
        print(self.stringify(value))

    def visitReturnStmt(self, stmt: Stmt.Return):
        value = None
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
        
        self.environment.define(stmt.name.lexeme, value)

    def visitWhileStmt(self, stmt: Stmt.While):
        self.loopLevel += 1
        while self.isTruthy(self.evaluate(stmt.condition)):
            try:
                self.execute(stmt.body)
            except breakError:
                break
            except continueError as error:
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
        from datetime import time # To check if variable holds a datetime.time object (return value of clock()).
        match object:
            case float(): # No check for int() since all values in Lox are saved as floats/doubles.
                return "number"
            case str():
                return "string"
            case bool(): # Fun fact: Bool is a subclass of int.
                return "boolean"
            case bytes():
                return "bytes"
            case LoxFunction():
                if object.declaration.name == None:
                    return "lambda"
                else:
                    return "function"
            case BuiltinFunction():
                return "native function"
            case List():
                return "list"
            case _ if isinstance(object, time): # Format to check Boolean conditions in match-case structure.
                return "datetime"
            case _ if isinstance(object, LoxInstance):
                return object.toString()[1:-1] # To avoid writing the <> twice.
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
        
        if (isinstance(object, LoxCallable)) or (type(object) == LoxInstance):
            return object.toString()
        
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
        import State
        if State.debugMode:
            return self.environment.get(name)

        distance = self.locals.get(expr, None)
        if distance != None:
            return self.environment.getAt(distance, name)
        else:
            # Check if variable is in the user-defined global scope.
            for env in self.varEnvs[-1]:
                if name.lexeme in env.values.keys():
                    return env.get(name)
            # We only fetch a variable's value if it is defined in the environment, i.e.,
            # its name is a key in the environment's value dictionary.
            # If the variable is undefined, we never try to fetch it, so no error is raised.
            # This addresses that.
            raise RuntimeError(name, f"Undefined variable or function '{name.lexeme}'.")
    
    def accessElements(self, object, start, end, expr: Expr.Access):
        if (type(start) != float) or (int(start) != start):
            raise RuntimeError(expr.operator, "Start index must be an integer.")
        
        if end != None:
            if (type(end) != float) or (int(end) != end):
                raise RuntimeError(expr.operator, "End index must be an integer.")

        if type(object) == str:
            length = len(object)
        elif type(object) == List:
            object = object.array
            length = len(object)
        if end == None: # Only accessing a single element.
            if (start >= 0) and (start < length):
                return object[int(start)]
            else:
                raise RuntimeError(expr.operator, "Index out of bounds.")
        else: # Possibly accessing a range.
            if (end >= 0) and (end < length):
                if (start >= 0) and (start <= length):
                    return object[int(start) : int(end) + 1]
                else:
                    raise RuntimeError(expr.operator, "Start index out of bounds.")
            else:
                raise RuntimeError(expr.operator, "End index out of bounds.")
    
    def evaluate(self, expr):
        return expr.accept(self)
    
    def visitAccessExpr(self, expr: Expr.Access):
        object = self.evaluate(expr.object)
        start = self.evaluate(expr.start)
        end = None
        if expr.end != None:
            end = self.evaluate(expr.end)
        
        if (type(object) == str):
            return self.accessElements(object, start, end, expr)
        elif (type(object) == List):
            output = self.accessElements(object, start, end, expr)
            if type(output) == list:
                return List(output)
            else:
                return output
        else:
            raise RuntimeError(expr.operator, "Member access only for strings and lists.")

    def visitAssignExpr(self, expr: Expr.Assign):
        value = self.evaluate(expr.value)

        distance = self.locals.get(expr, None)
        if distance != None:
            self.environment.assignAt(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visitBinaryExpr(self, expr: Expr.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.GREATER:
                self.checkNumberOperands(expr.operator, left, right)
                return (float(left) > float(right))
            case TokenType.GREATER_EQUAL:
                self.checkNumberOperands(expr.operator, left, right)
                return (float(left) >= float(right))
            case TokenType.LESS:
                self.checkNumberOperands(expr.operator, left, right)
                return (float(left) < float(right))
            case TokenType.LESS_EQUAL:
                self.checkNumberOperands(expr.operator, left, right)
                return (float(left) <= float(right))
            case TokenType.BANG_EQUAL:
                return (type(left) != type(right) or (left != right))
            case TokenType.EQUAL_EQUAL:
                return (type(left) == type(right) and (left == right))
            case TokenType.MINUS:
                self.checkNumberOperands(expr.operator, left, right)
                return (float(left) - float(right))
            case TokenType.PLUS:
                if (type(left) == List) and (type(right) == List):
                    return List(left.array + right.array)

                if (type(left) == float) and (type(right) == float):
                    return (float(left) + float(right))
                
                if (type(left) == str) and (type(right) == str):
                    return (str(left) + str(right))
                
                # Allows for concatenation of a string and a non-numeric variable as well.
                if type(left) == str:
                    return str(left) + self.stringify(right)
                
                if type(right) == str:
                    return self.stringify(left) + str(right)
                
                raise RuntimeError(expr.operator, 
                                   "Cannot add given operands.")
            case TokenType.SLASH:
                self.checkNumberOperands(expr.operator, left, right)
                # Comparison with 0 works even for floats.
                if float(right) == 0:
                    raise RuntimeError(expr.operator, "Division by zero not allowed.")
                return (float(left) / float(right))
            case TokenType.STAR:
                if type(left) == str:
                    if type(right) == float:
                        if int(right) == right:
                            return left * int(right)
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
                            return right * int(left)
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
            case TokenType.MOD:
                self.checkNumberOperands(expr.operator, left, right)
                return (float(left) % float(right))
            case TokenType.POWER:
                self.checkNumberOperands(expr.operator, left, right)
                # Note: Python evaluates 0^0 as 1.
                return (float(left) ** float(right))

    def visitCallExpr(self, expr: Expr.Call):
        callee = self.evaluate(expr.callee)

        arguments = list()
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        
        if not isinstance(callee, LoxCallable):
            raise RuntimeError(expr.paren, "No such function or class.")
        
        if len(arguments) != callee.arity():
            if callee.arity() == 1: # To make argument singular rather than plural (plural for 0 as well).
                raise RuntimeError(expr.paren, 
                               f"Expected {callee.arity()} argument but got {len(arguments)}.")
            else:
                raise RuntimeError(expr.paren, 
                               f"Expected {callee.arity()} arguments but got {len(arguments)}.")
        
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
            return object.get(expr.name)
        
        raise RuntimeError(expr.name, "Only instances have properties.")

    def visitGroupingExpr(self, expr: Expr.Grouping):
        return self.evaluate(expr.expression)

    # Lambdas can all be given default name None since they are accessed by index in the parameter/argument list, not by name.
    def visitLambdaExpr(self, expr: Expr.Lambda):
        lambdaDeclaration = Stmt.Function(None, expr.params, expr.body)
        return LoxFunction(lambdaDeclaration, self.environment, False)

    def visitLiteralExpr(self, expr: Expr.Literal):
        return expr.value
    
    def visitListExpr(self, expr: Expr.List):
        elements = []
        for element in expr.elements:
            elements.append(self.evaluate(element))
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
        mod = self.evaluate(expr.part.object)
        start = self.evaluate(expr.part.start)
        end = None
        if expr.part.end != None:
            end = self.evaluate(expr.part.end)

        if type(mod) == str:
            # Strings in Python are immutable.
            # They, thus, do not support direct item assignment.
            # Thus, we turn the string into a list of its characters,
            # make our modifications, and put it back together.
            tempList = list(mod)
            if end == None:
                tempList[int(start)] = value
            else:
                tempList[int(start) : int(end) + 1] = value
            mod = "".join(tempList)
        elif type(mod) == List:
            if end == None:
                mod.array[int(start)] = value
            else:
                mod.array[int(start) : int(end) + 1] = value
        name = expr.part.object.name
        self.environment.assign(name, mod)
        return mod
    
    def visitSetExpr(self, expr: Expr.Set):
        object = self.evaluate(expr.object)

        if (isinstance(object, LoxInstance)) or (type(object) == List):
            value = self.evaluate(expr.value)
            object.set(expr.name, value)
            return value
        
        raise RuntimeError(expr.name, "Only instances have fields.")
    
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