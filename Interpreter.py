from Token import Token, TokenType
from Expr import Expr
from Stmt import Stmt
from Environment import Environment
from LoxCallable import LoxCallable
from LoxFunction import LoxFunction
from LoxClass import LoxClass
from LoxInstance import LoxInstance
from BuiltinFunction import BuiltinFunction
from Error import RuntimeError, breakError, continueError, Return
from Debug import breakpointStop

class Interpreter:
    globals = Environment()
    environment = globals
    loopLevel = 0
    locals = dict()

    from BuiltinFunction import builtinSetUp
    builtinSetUp()
    from BuiltinFunction import builtins

    from Modules.userIO import userIOSetUp
    userIOSetUp()
    from Modules.userIO import userIO

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
    
    def executeBlock(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    # No need to check that 'break' or 'continue' are inside a loop, since their presence outside one raises a Parse Error (before the interpreter phase).
    # Making it a Parse Error rather than a Runtime Error avoids the case where 'break' and 'continue' are placed inside the block after a false condition; the program will never run those statements, so no error gets raised (despite it being bad code).
    def visitBreakStmt(self, stmt: Stmt.Break):
        raise breakError(stmt.breakCMD, stmt.loopType)

    def visitBlockStmt(self, stmt: Stmt.Block):
        self.executeBlock(stmt.statements, Environment(self.environment))
    
    def visitClassStmt(self, stmt: Stmt.Class):
        self.environment.define(stmt.name.lexeme, None)

        methods = dict()
        for method in stmt.methods:
            function = LoxFunction(method, self.environment)
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
        if (type(stmt.expression) != Expr.Assign) and (type(stmt.expression) != Expr.Set):
            self.visitPrintStmt(Stmt.Print(stmt.expression))
        
        else:
            self.evaluate(stmt.expression)

    def visitFunctionStmt(self, stmt: Stmt.Function):
        # Check that function is not an unassigned lambda (do nothing if it is).
        if stmt.name != None:
            function = LoxFunction(stmt, self.environment)
            self.environment.define(stmt.name.lexeme, function)

    def visitIfStmt(self, stmt: Stmt.If):
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch != None:
            self.execute(stmt.elseBranch)

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
            case _ if isinstance(object, time): # Format to check Boolean conditions in match-case structure.
                return "datetime"
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
            if name.lexeme in self.globals.values.keys():
                return self.globals.get(name)
            if name.lexeme in self.userIO.values.keys():
                return self.userIO.get(name)
            return self.builtins.get(name)
    
    def evaluate(self, expr):
        return expr.accept(self)

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
                                   "Operands must consist of a number or a string.")
            case TokenType.SLASH:
                self.checkNumberOperands(expr.operator, left, right)
                # Comparison with 0 works even for floats.
                if float(right) == 0:
                    raise RuntimeError(expr.operator, "Division by zero not allowed.")
                return (float(left) / float(right))
            case TokenType.STAR:
                self.checkNumberOperands(expr.operator, left, right)
                return (float(left) * float(right))
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
            raise RuntimeError(expr.paren, "Can only call functions and classes.")
        
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
        if isinstance(object, LoxInstance):
            return object.get(expr.name)
        
        raise RuntimeError(expr.name, "Only instances have properties.")

    def visitGroupingExpr(self, expr: Expr.Grouping):
        return self.evaluate(expr.expression)

    # Lambdas can all be given default name None since they are accessed by index in the parameter/argument list, not by name.
    def visitLambdaExpr(self, expr: Expr.Lambda):
        lambdaDeclaration = Stmt.Function(None, expr.params, expr.body)
        return LoxFunction(lambdaDeclaration, self.environment)

    def visitLiteralExpr(self, expr):
        return expr.value
    
    def visitLogicalExpr(self, expr: Expr.Logical):
        left = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.isTruthy(left):
                return left
        else:
            if not self.isTruthy(left):
                return left
        
        return self.evaluate(expr.right)
    
    def visitSetExpr(self, expr: Expr.Set):
        object = self.evaluate(expr.object)

        if isinstance(object, LoxInstance):
            value = self.evaluate(expr.value)
            object.set(expr.name, value)
            return value
        
        raise RuntimeError(expr.name, "Only instances have fields.")
    
    # Ternary implementation my own.
    def visitTernaryExpr(self, expr: Expr.Ternary):
        if self.isTruthy(self.evaluate(expr.condition)):
            return self.evaluate(expr.trueBranch)
        return self.evaluate(expr.falseBranch)

    def visitUnaryExpr(self, expr: Expr.Unary):
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.BANG:
                return not self.isTruthy(right)
            case MINUS:
                self.checkNumberOperand(expr.operator, right)
                return -1 * float(right)
        
        return None

    def visitVariableExpr(self, expr: Expr.Variable):
        return self.lookUpVariable(expr.name, expr)