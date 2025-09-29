from Expr import Expr
from Stmt import Stmt
from Token import Token, TokenType
from Error import StaticError
from enum import Enum
from Interpreter import Interpreter
from Warning import unusedWarning

class Resolver:
    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter = interpreter
        self.scopes: list[dict[Token, bool]] = []
        self.FunctionType = Enum('FunctionType', 'NONE, FUNCTION, LAMBDA, INITIALIZER, METHOD')
        self.classType = Enum('classType', 'NONE, CLASS, SUBCLASS')
        self.currentFunction = self.FunctionType.NONE
        self.currentClass = self.classType.NONE
        # Will record all the defined variables (until they are used) and their line of declaration.
        # Once the variable is used somewhere, it is removed from the dictionary.
        self.localVars: dict[Token, tuple[int, bool]] = {}
        # Flag variable marking that we are resolving an assignment expression.
        # If true, resolving a variable will not mark it as having been "used".
        # Therefore, only assigning to a variable will not be sufficient to avoid a warning (must use the variable somewhere).
        self.inAssign = False
        # Flag variable marking that we are resolving a declaration in a group.
        # Variables do not have to be used in a group.
        # Silence "unused variable" warning.
        self.inGroup = False
    
    def beginScope(self) -> None:
        self.scopes.append(dict())
    
    def endScope(self) -> None:
        self.scopes.pop()
    
    def declare(self, name: Token) -> None:
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
        if self.inGroup:
            self.localVars[name][1] = True

    def define(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return
        
        self.scopes[-1][name] = True

    def resolve(self, target: Expr | Stmt | list[Stmt]) -> None:
        if type(target) == list:
            for statement in target:
                self.resolve(statement)
        else:
            try:
                target.accept(self)
            except StaticError as error:
                error.show()
    
    def resolveLocal(self, expr: Expr.Variable, name: Token) -> None:
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
    
    def resolveFunction(self, function: Stmt.Function, funcType) -> None:
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
    
    def resolveLambda(self, expr: Expr.Lambda, lambdaType) -> None:
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

    def varWarnings(self, varList: dict) -> None:
        # Filter out any variables that have been used.
        varList = {x:varList[x] for x in varList if varList[x][1] != True}

        # Sort variables by line of declaration.
        varList = {entry: varList[entry] for entry in sorted(varList, key=varList.get)}

        # Issue the warnings.
        for var in varList:
            unusedWarning(var).warn()
    
    def visitBreakStmt(self, stmt: Stmt.Break) -> None:
        pass
    
    def visitBlockStmt(self, stmt: Stmt.Block) -> None:
        self.beginScope()
        self.resolve(stmt.statements)
        self.endScope()
    
    def visitClassStmt(self, stmt: Stmt.Class) -> None:
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
    
    def visitContinueStmt(self, stmt: Stmt.Continue) -> None:
        pass

    def visitErrorStmt(self, stmt: Stmt.Error) -> None:
        self.resolve(stmt.body)
        self.resolve(stmt.handler)

    def visitExpressionStmt(self, stmt: Stmt.Expression) -> None:
        self.resolve(stmt.expression)
    
    def visitFetchStmt(self, stmt: Stmt.Fetch) -> None:
        pass
    
    def visitFunctionStmt(self, stmt: Stmt.Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolveFunction(stmt, self.FunctionType.FUNCTION)
    
    def visitGroupStmt(self, stmt: Stmt.Group) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)

        previous = self.inGroup
        self.inGroup = True
        self.beginScope()
        for statement in stmt.vars:
            self.resolve(statement)
        for statement in stmt.functions:
            self.resolve(statement)
        for statement in stmt.classes:
            self.resolve(statement)
        self.endScope()
        self.inGroup = previous
    
    def visitIfStmt(self, stmt: Stmt.If) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if stmt.elseBranch != None:
            self.resolve(stmt.elseBranch)
    
    def visitListStmt(self, stmt: Stmt.List) -> None:
        self.declare(stmt.name)
        if stmt.initializer != None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visitMatchStmt(self, stmt: Stmt.Match) -> None:
        self.resolve(stmt.value)
        for case in stmt.cases:
            self.resolve(case["value"]) # Value.
            self.resolve(case["stmt"]) # Statement.
    
    def visitPrintStmt(self, stmt: Stmt.Print) -> None:
        self.resolve(stmt.expression)
    
    def visitReportStmt(self, stmt: Stmt.Report) -> None:
        self.resolve(stmt.exception)

    def visitReturnStmt(self, stmt: Stmt.Return) -> None:
        if self.currentFunction == self.FunctionType.NONE:
            raise StaticError(stmt.keyword, "Cannot return from top-level code.")
        
        if stmt.value != None:
            if self.currentFunction == self.FunctionType.INITIALIZER:
                raise StaticError(stmt.keyword, 
                                   "Cannot return a value from an initializer.")
            self.resolve(stmt.value)
    
    def visitVarStmt(self, stmt: Stmt.Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer != None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
    
    def visitWhileStmt(self, stmt: Stmt.While) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visitAccessExpr(self, expr: Expr.Access) -> None:
        self.resolve(expr.start)
        if expr.end != None:
            self.resolve(expr.end)
        self.resolve(expr.object)

    def visitAssignExpr(self, expr: Expr.Assign) -> None:
        self.resolve(expr.value)

        self.inAssign = True
        self.resolveLocal(expr, expr.name)
        self.inAssign = False
    
    def visitBinaryExpr(self, expr: Expr.Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    def visitCallExpr(self, expr: Expr.Call) -> None:
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)
        
    def visitCommaExpr(self, expr: Expr.Comma) -> None:
        for expression in expr.expressions:
            self.resolve(expression)
    
    def visitGetExpr(self, expr: Expr.Get) -> None:
        self.resolve(expr.object)
    
    def visitGroupingExpr(self, expr: Expr.Grouping) -> None:
        self.resolve(expr.expression)
    
    def visitLambdaExpr(self, expr: Expr.Lambda) -> None:
        self.resolveLambda(expr, self.FunctionType.LAMBDA)

    def visitListExpr(self, expr: Expr.List) -> None:
        for element in expr.elements:
            self.resolve(element)
    
    def visitLiteralExpr(self, expr: Expr.Literal) -> None:
        pass

    def visitLogicalExpr(self, expr: Expr.Logical) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    def visitModifyExpr(self, expr: Expr.Modify) -> None:
        self.resolve(expr.value)
        self.resolve(expr.part)
    
    def visitSetExpr(self, expr: Expr.Set) -> None:
        self.resolve(expr.value)
        self.resolve(expr.object)
    
    def visitSuperExpr(self, expr: Expr.Super) -> None:
        if self.currentClass == self.classType.NONE:
            raise StaticError(expr.keyword, 
                               "Can't use 'super' outside of a class.")
        elif self.currentClass == self.classType.CLASS:
            raise StaticError(expr.keyword,
                               "Can't use 'super' in a class with no superclass.")
        
        self.resolveLocal(expr, expr.keyword)
    
    def visitTernaryExpr(self, expr: Expr.Ternary) -> None:
        self.resolve(expr.condition)
        self.resolve(expr.trueBranch)
        self.resolve(expr.falseBranch)
    
    def visitThisExpr(self, expr: Expr.This) -> None:
        if self.currentClass == self.classType.NONE:
            raise StaticError(expr.keyword, "Cannot use 'this' outside of a class.")

        self.resolveLocal(expr, expr.keyword)
    
    def visitUnaryExpr(self, expr: Expr.Unary) -> None:
        self.resolve(expr.right)
    
    def visitVariableExpr(self, expr: Expr.Variable) -> None:
        if len(self.scopes) != 0:
            # Check that variable in expression is declared (but not yet defined) in current scope.
            scope = self.scopes[-1]
            for key in scope.keys():
                if (key.lexeme == expr.name.lexeme) and (scope.get(key, None) == False):
                    raise StaticError(expr.name, "Cannot read local variable in its own initializer.")
        
        self.resolveLocal(expr, expr.name)