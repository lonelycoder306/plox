from Expr import Expr
from Stmt import Stmt
from Token import Token
from Error import ResolveError
from enum import Enum
from Interpreter import Interpreter
from Warning import unusedWarning

class Resolver:
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes = list()
        self.FunctionType = Enum('FunctionType', 'NONE, FUNCTION, LAMBDA')
        self.currentFunction = self.FunctionType.NONE
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
        
        if name.lexeme in self.scopes[-1].keys():
            ResolveError(name, "Already a variable with this name in this scope.").show()
        
        self.scopes[-1][name] = False
        # Add the token instead of the lexeme in case its fields are required for error-reporting.
        self.localVars[name] = [name.line, False] # False = has not been used in this scope; using a list since a tuple is immutable.

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
            except ResolveError as error:
                error.show()
    
    def resolveLocal(self, expr: Expr, name: Token):
        for i in range(len(self.scopes) - 1, -1, -1): # -1 increment to iterate in reverse
            for key in self.scopes[-1].keys():
                if key.lexeme == name.lexeme:
                    self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                    if not self.inAssign:
                        self.localVars[key][1] = True # True = has been used in this scope (in other than an assignment).
                    return
    
    def resolveFunction(self, function: Stmt.Function, type):
        enclosingFunction = self.currentFunction
        self.currentFunction = type
        self.beginScope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.endScope()
        self.currentFunction = enclosingFunction
    
    def resolveLambda(self, expr: Expr.Lambda, type):
        enclosingLambda = self.currentFunction
        self.currentFunction = type
        self.beginScope()
        for param in expr.params:
            self.declare(param)
            self.define(param)
        self.resolve(expr.body)
        self.endScope()
        self.currentFunction = enclosingLambda

    def varWarnings(self, varList: list):
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
    
    def visitContinueStmt(self, stmt: Stmt.Continue):
        pass

    def visitExpressionStmt(self, stmt: Stmt.Expression):
        self.resolve(stmt.expression)
    
    def visitFunctionStmt(self, stmt: Stmt.Function):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolveFunction(stmt, self.FunctionType.FUNCTION)
    
    def visitIfStmt(self, stmt: Stmt.If):
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if stmt.elseBranch != None:
            self.resolve(stmt.elseBranch)
    
    def visitPrintStmt(self, stmt: Stmt.Print):
        self.resolve(stmt.expression)
    
    def visitReturnStmt(self, stmt: Stmt.Return):
        if self.currentFunction == self.FunctionType.NONE:
            raise ResolveError(stmt.keyword, "Can't return from top-level code.")
        
        if stmt.value != None:
            self.resolve(stmt.value)
    
    def visitVarStmt(self, stmt: Stmt.Var):
        self.declare(stmt.name)
        if stmt.initializer != None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
    
    def visitWhileStmt(self, stmt: Stmt.While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

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
    
    def visitGroupingExpr(self, expr: Expr.Grouping):
        self.resolve(expr.expression)
    
    def visitLambdaExpr(self, expr: Expr.Lambda):
        self.resolveLambda(expr, self.FunctionType.LAMBDA)
    
    def visitLiteralExpr(self, expr: Expr.Literal):
        pass

    def visitLogicalExpr(self, expr: Expr.Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    def visitTernaryExpr(self, expr: Expr.Ternary):
        self.resolve(expr.condition)
        self.resolve(expr.trueBranch)
        self.resolve(expr.falseBranch)
    
    def visitUnaryExpr(self, expr: Expr.Unary):
        self.resolve(expr.right)
    
    def visitVariableExpr(self, expr: Expr.Variable):
        if ((len(self.scopes) != 0) 
            and (expr.name in self.scopes[-1].keys()) 
            and (self.scopes[-1].get(expr.name, None) == False)):
                raise ResolveError(expr.name, "Can't read local variable in its own initializer.")
        
        self.resolveLocal(expr, expr.name)