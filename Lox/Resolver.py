from Expr import Expr
from Stmt import Stmt
from Token import Token, TokenType
from Error import StaticError
from enum import Enum
from Interpreter import Interpreter
from Warning import unusedWarning

class Resolver:
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes = list()
        self.FunctionType = Enum('FunctionType', 'NONE, FUNCTION, LAMBDA, INITIALIZER, METHOD')
        self.classType = Enum('classType', 'NONE, CLASS, SUBCLASS')
        self.currentFunction = self.FunctionType.NONE
        self.currentClass = self.classType.NONE
        # Will record all the defined variables (until they are used) and their line of declaration.
        # Once the variable is used somewhere, it is removed from the dictionary.
        self.localVars = dict()
        # Flag variable marking that we are resolving an assignment expression.
        # If true, resolving a variable will not mark it as having been "used".
        # Therefore, only assigning to a variable will not be sufficient to avoid a warning (must use the variable somewhere).
        self.inAssign = False
    
    def beginScope(self):
        self.scopes.append(dict())
    
    def endScope(self):
        self.scopes.pop()
    
    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return
        
        scope = self.scopes[-1]
        for key in scope.keys():
            if key.lexeme == name.lexeme:
                raise StaticError(name, "Already a variable with this name in this scope.")
        
        scope[name] = False
        # Add the token instead of the lexeme in case its fields are required for error-reporting.
        # False = has not been used in this scope; using a list since a tuple is immutable.
        self.localVars[name] = [name.line, False]

    def define(self, name: Token):
        if len(self.scopes) == 0:
            return
        
        self.scopes[-1][name] = True

    def resolve(self, target: Expr | Stmt | list[Stmt]):
        if type(target) == list:
            for statement in target:
                self.resolve(statement)
        else:
            try:
                target.accept(self)
            except StaticError as error:
                error.show()
    
    def resolveLocal(self, expr: Expr, name: Token):
        size = len(self.scopes)

        for i in range(size - 1, -1, -1): # -1 increment to iterate in reverse
            for key in self.scopes[i].keys():
                if key.lexeme == name.lexeme:
                    self.interpreter.resolve(expr, size - 1 - i)
                    if not self.inAssign:
                        # True = has been used in this scope 
                        # (in other than an assignment).
                        self.localVars[key][1] = True
                    return
    
    def resolveFunction(self, function: Stmt.Function, funcType):
        enclosingFunction = self.currentFunction
        self.currentFunction = funcType

        self.beginScope()
        if function.params != None:
            for param in function.params:
                if (type(param) == Token) and (param.type != TokenType.ELLIPSIS):
                    self.declare(param)
                    self.define(param)
                elif type(param) == Expr.Assign:
                    self.declare(param.name)
                    self.define(param.name)
        self.resolve(function.body)
        self.endScope()

        self.currentFunction = enclosingFunction
    
    def resolveLambda(self, expr: Expr.Lambda, lambdaType):
        enclosingLambda = self.currentFunction
        self.currentFunction = lambdaType

        self.beginScope()
        for param in expr.params:
            if (type(param) == Token) and (param.type != TokenType.ELLIPSIS):
                    self.declare(param)
                    self.define(param)
            elif type(param) == Expr.Assign:
                self.declare(param.name)
                self.define(param.name)
        self.resolve(expr.body)
        self.endScope()

        self.currentFunction = enclosingLambda

    def varWarnings(self, varList: dict):
        # Filter out any variables that have been used.
        varList = {x:varList[x] for x in varList if varList[x][1] != True}

        # Sort variables by line of declaration.
        varList = {entry: varList[entry] for entry in sorted(varList, key=varList.get)}

        # Issue the warnings.
        for var in varList:
            unusedWarning(var).warn()
    
    def visitBreakStmt(self, stmt: Stmt.Break):
        pass
    
    def visitBlockStmt(self, stmt: Stmt.Block):
        self.beginScope()
        self.resolve(stmt.statements)
        self.endScope()
    
    def visitClassStmt(self, stmt: Stmt.Class):
        enclosingClass = self.currentClass
        self.currentClass = self.classType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if ((stmt.superclass != None) and 
            (stmt.name.lexeme == stmt.superclass.name.lexeme)):
            raise RuntimeError(stmt.superclass.name, "A class cannot inherit from itself.")

        if stmt.superclass != None:
            self.currentClass = self.classType.SUBCLASS
            self.resolve(stmt.superclass)
        
        if stmt.superclass != None:
            self.beginScope()
            dummySuper = Token(TokenType.SUPER, "super", 
                                str("super"), 0, 0, None)
            self.declare(dummySuper)
            self.define(dummySuper)
            # To avoid getting an "unused local variable" warning 
            # when adding a superclass.
            self.localVars[dummySuper][1] = True

        self.beginScope()
        dummyThis = Token(TokenType.THIS, "this", str("this"), 0, 0, None)
        self.declare(dummyThis)
        self.define(dummyThis)
        # To avoid getting an "unused local variable" warning 
        # when defining a class.
        self.localVars[dummyThis][1] = True

        for method in stmt.classMethods:
            self.beginScope()
            dummyThis = Token(TokenType.THIS, "this", str("this"), 0, 0, None)
            self.declare(dummyThis)
            self.define(dummyThis)
            self.localVars[dummyThis][1] = True
            self.resolveFunction(method, self.FunctionType.METHOD)
            self.endScope()

        for method in stmt.private:
            declaration = self.FunctionType.METHOD
            if method.name.lexeme == "init":
                raise StaticError(method.name, "Class constructor cannot be made private.")
            self.resolveFunction(method, declaration)
        
        for method in stmt.public:
            declaration = self.FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = self.FunctionType.INITIALIZER
            self.resolveFunction(method, declaration)
        
        self.endScope()

        if stmt.superclass != None:
            self.endScope()

        self.currentClass = enclosingClass
    
    def visitContinueStmt(self, stmt: Stmt.Continue):
        pass

    def visitErrorStmt(self, stmt: Stmt.Error):
        self.resolve(stmt.body)
        self.resolve(stmt.handler)

    def visitExpressionStmt(self, stmt: Stmt.Expression):
        self.resolve(stmt.expression)
    
    def visitFetchStmt(self, stmt: Stmt.Fetch):
        pass
    
    def visitFunctionStmt(self, stmt: Stmt.Function):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolveFunction(stmt, self.FunctionType.FUNCTION)
    
    def visitGroupStmt(self, stmt: Stmt.Group):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.beginScope()
        for statement in stmt.vars:
            self.resolve(statement)
        for statement in stmt.functions:
            self.resolve(statement)
        for statement in stmt.classes:
            self.resolve(statement)
        self.endScope()
    
    def visitIfStmt(self, stmt: Stmt.If):
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if stmt.elseBranch != None:
            self.resolve(stmt.elseBranch)
    
    def visitListStmt(self, stmt: Stmt.List):
        self.declare(stmt.name)
        if stmt.initializer != None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
    
    def visitPrintStmt(self, stmt: Stmt.Print):
        self.resolve(stmt.expression)
    
    def visitReportStmt(self, stmt: Stmt.Report):
        self.resolve(stmt.exception)

    def visitReturnStmt(self, stmt: Stmt.Return):
        if self.currentFunction == self.FunctionType.NONE:
            raise StaticError(stmt.keyword, "Cannot return from top-level code.")
        
        if stmt.value != None:
            if self.currentFunction == self.FunctionType.INITIALIZER:
                raise StaticError(stmt.keyword, 
                                   "Cannot return a value from an initializer.")
            self.resolve(stmt.value)
    
    def visitVarStmt(self, stmt: Stmt.Var):
        self.declare(stmt.name)
        if stmt.initializer != None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
    
    def visitWhileStmt(self, stmt: Stmt.While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visitAccessExpr(self, expr: Expr.Access):
        self.resolve(expr.start)
        if expr.end != None:
            self.resolve(expr.end)
        self.resolve(expr.object)

    def visitAssignExpr(self, expr: Expr.Assign):
        self.resolve(expr.value)

        self.inAssign = True
        self.resolveLocal(expr, expr.name)
        self.inAssign = False
    
    def visitBinaryExpr(self, expr: Expr.Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    def visitCallExpr(self, expr: Expr.Call):
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)
        
    def visitCommaExpr(self, expr: Expr.Comma):
        for expression in expr.expressions:
            self.resolve(expression)
    
    def visitGetExpr(self, expr: Expr.Get):
        self.resolve(expr.object)
    
    def visitGroupingExpr(self, expr: Expr.Grouping):
        self.resolve(expr.expression)
    
    def visitLambdaExpr(self, expr: Expr.Lambda):
        self.resolveLambda(expr, self.FunctionType.LAMBDA)

    def visitListExpr(self, expr: Expr.List):
        for element in expr.elements:
            self.resolve(element)
    
    def visitLiteralExpr(self, expr: Expr.Literal):
        pass

    def visitLogicalExpr(self, expr: Expr.Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    def visitModifyExpr(self, expr: Expr.Modify):
        self.resolve(expr.value)
        self.resolve(expr.part)
    
    def visitSetExpr(self, expr: Expr.Set):
        self.resolve(expr.value)
        self.resolve(expr.object)
    
    def visitSuperExpr(self, expr: Expr.Super):
        if self.currentClass == self.classType.NONE:
            raise StaticError(expr.keyword, 
                               "Can't use 'super' outside of a class.")
        elif self.currentClass == self.classType.CLASS:
            raise StaticError(expr.keyword,
                               "Can't use 'super' in a class with no superclass.")
        
        self.resolveLocal(expr, expr.keyword)
    
    def visitTernaryExpr(self, expr: Expr.Ternary):
        self.resolve(expr.condition)
        self.resolve(expr.trueBranch)
        self.resolve(expr.falseBranch)
    
    def visitThisExpr(self, expr: Expr.This):
        if self.currentClass == self.classType.NONE:
            raise StaticError(expr.keyword, "Cannot use 'this' outside of a class.")

        self.resolveLocal(expr, expr.keyword)
    
    def visitUnaryExpr(self, expr: Expr.Unary):
        self.resolve(expr.right)
    
    def visitVariableExpr(self, expr: Expr.Variable):
        if len(self.scopes) != 0:
            # Check that variable in expression is declared (but not yet defined) in current scope.
            scope = self.scopes[-1]
            for key in scope.keys():
                if (key.lexeme == expr.name.lexeme) and (scope.get(key, None) == False):
                    raise StaticError(expr.name, "Cannot read local variable in its own initializer.")
        
        self.resolveLocal(expr, expr.name)