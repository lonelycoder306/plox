from typing import Any

from Token import TokenType, Token
from Expr import Expr
from Stmt import Stmt
from Error import ParseError
from Warning import returnWarning
from String import String

class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.current = 0
        self.tokens = tokens
        # Will be None when not in a loop, "forLoop" when within a for-loop, 
        # and "whileLoop" when within a while-loop.
        self.loopType: str | None = None
        self.loopLevel = 0
        # To turn off "code after return statement" warnings if braces
        # aren't used after a control-structure statement.
        self.inStructure = False
        # To check that we are in a constructor when declaring private
        # fields.
        self.inClass = False
        self.inInit = False
    
    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.isAtEnd():
            try:
                statements.append(self.declaration())
            except ParseError as error:
                self.synchronize()
                error.show()
        
        return statements
    
    def declaration(self) -> Stmt:
        # Moved the try-catch block from here to parse() instead.
        # Avoid the inclusion of None-value declarations in the statement list.

        if self.match(TokenType.CLASS):
            return self.classDeclaration()

        if self.match(TokenType.FUN):
            if self.check(TokenType.IDENTIFIER):
                return self.function("function")
            # Signal that the function is an unassigned lambda (so interpreter does nothing with it).
            return self.function("lambda")
        
        if self.match(TokenType.VAR):
            return self.varDeclaration("VAR")
        
        if self.match(TokenType.FIX):
            return self.varDeclaration("FIX")
        
        if self.match(TokenType.LIST):
            return self.listDeclaration()
        
        if self.match(TokenType.GROUP):
            return self.groupDeclaration()
        
        if self.match(TokenType.SAFE):
            if self.inInit:
                return self.safeDeclaration()
            else:
                raise ParseError(self.previous(),
                                 "Cannot use modifier 'safe' outside a constructor.")
        
        return self.statement()
            
    def statement(self) -> Stmt:
        if self.match(TokenType.ATTEMPT):
            return self.errorStatement()
        if self.match(TokenType.BREAK):
            return self.breakStatement()
        if self.match(TokenType.CONTINUE):
            return self.continueStatement()
        if self.match(TokenType.FOR):
            return self.forStatement()
        if self.match(TokenType.GET):
            return self.fetchStatement()
        if self.match(TokenType.IF):
            return self.ifStatement()
        if self.match(TokenType.MATCH):
            return self.matchStruct()
        if self.match(TokenType.PRINT):
            return self.printStatement()
        if self.match(TokenType.REPORT):
            return self.reportStatement()
        if self.match(TokenType.RETURN):
            return self.returnStatement()
        if self.match(TokenType.WHILE):
            return self.whileStatement()
        if self.match(TokenType.LEFT_BRACE):
            return Stmt.Block(self.block())

        return self.expressionStatement()

    def breakStatement(self) -> Stmt.Break:
        breakToken = self.previous()
        if self.loopLevel == 0:
            raise ParseError(breakToken, "Cannot have 'break' outside loop.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return Stmt.Break(breakToken, self.loopType)
    
    def classDeclaration(self) -> Stmt.Class:
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")

        superclass = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Expr.Variable(self.previous())
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        previousClass = self.inClass
        self.inClass = True
        private = list()
        public = list()
        classMethods = list()
        while (not self.check(TokenType.RIGHT_BRACE)) and (not self.isAtEnd()):
            if self.match(TokenType.CLASS):
                classMethods.append(self.function("method"))
            elif self.match(TokenType.SAFE):
                private.append(self.function("method"))
            else:
                public.append(self.function("method"))

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        self.inClass = previousClass

        return Stmt.Class(name, superclass, private, public, classMethods)

    def continueStatement(self) -> Stmt.Continue:
        continueToken = self.previous()
        if self.loopLevel == 0:
            raise ParseError(continueToken, "Cannot have 'continue' outside loop.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return Stmt.Continue(continueToken, self.loopType)

    def errorStatement(self) -> Stmt.Error:
        body = self.declaration()
        self.consume(TokenType.HANDLE, "Attempt statement must have a handler.")
        errors = None
        if self.match(TokenType.LEFT_PAREN):
            errors = []
            while not self.check(TokenType.RIGHT_PAREN):
                error = self.primary()
                if type(error) != Expr.Variable:
                    raise RuntimeError(self.previous(), "Invalid error type.")
                errors.append(error)
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after error types.")
        handler = self.declaration()
        return Stmt.Error(body, errors, handler)
    
    def fetchStatement(self) -> Stmt.Fetch:
        mode = self.previous()
        name = self.consume(TokenType.STRING, "Expect name of import.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after fetch statement.")

        if mode.lexeme[3:] == "Lib":
            from Scanner import Scanner
            file = "Libraries/" + name.lexeme[1:-1] + ".lox"
            try:
                with open(file, "r") as f:
                    text = f.read()
                f.close()
                import State as State
                with open(file, "r") as f:
                    lines = f.readlines()
                    lines = [line.rstrip() for line in lines]
                    State.fileLines[file] = lines
            except FileNotFoundError:
                raise ParseError(name, "No such library file.")
            scanner = Scanner(text, file)
            newTokens = scanner.scanTokens()[:-1]
            self.tokens[self.current:self.current] = newTokens

        elif mode.lexeme[3:] == "File":
            from Scanner import Scanner
            file = name.lexeme[1:-1]
            if (len(file) < 4) or (file[-4:] != ".lox"):
                raise ParseError(name, "Invalid Lox file.")
            try:
                with open(file, "r") as f:
                    text = f.read()
                f.close()
                import State as State
                with open(file, "r") as f:
                    lines = f.readlines()
                    lines = [line.rstrip() for line in lines]
                    State.fileLines[file] = lines
            except FileNotFoundError:
                raise ParseError(name, "File not found.")
            scanner = Scanner(text, file)
            newTokens = scanner.scanTokens()[:-1]
            self.tokens[self.current:self.current] = newTokens

        return Stmt.Fetch(mode, name)

    def rangeForLoop(self, initType) -> Stmt.Block:
        iterator = self.consume(TokenType.IDENTIFIER, "Expect iterator variable name.")
        colon = self.advance()
        iterableVar = None
        if self.check(TokenType.IDENTIFIER):
            iterable = self.advance()
            iterableVar = Expr.Variable(iterable)
        elif self.check(TokenType.LEFT_BRACKET):
            iterableVar = self.listExpr()
        elif self.match(TokenType.STRING):
            iterableVar = Expr.Literal(String(self.previous().literal))
        else:
            raise ParseError(self.peek(), "Expect iterable object.")
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after iteration clause.")

        # var __UNUSED__VAR = 0;
        indexToken = Token(TokenType.IDENTIFIER, "__UNUSED__VAR", None, 0, 0, "")
        indexInit = Expr.Literal(float(0))
        # We use the colon as our "blame token" in case any errors occur
        # and need to be reported.
        # It replaces the actual tokens that should be in many of these nodes.
        # We can't make and use fake tokens since they need to exist in the actual
        # text of the code if reporting occurs.
        indexDecl = Stmt.Var(indexToken, colon, indexInit, "VAR")

        # var i = array[0]; (example)
        iteratorInit = Expr.Access(iterableVar, colon, Expr.Literal(float(0)), None)
        iteratorDecl = None
        if initType == "var":
            iteratorDecl = Stmt.Var(iterator, colon, iteratorInit, "VAR")
        elif initType == "assign":
            iteratorDecl = Stmt.Expression(Expr.Assign(iterator, colon, iteratorInit))
        
        # __UNUSED__VAR < length(array) (example)
        compareLeft = Expr.Variable(indexToken)
        compareToken = Token(TokenType.LESS, "<", None, 0, 0, "")
        calleeToken = Token(TokenType.IDENTIFIER, "length", None, 0, 0, "")
        callee = Expr.Variable(calleeToken)
        compareRight = Expr.Call(callee, colon, colon, [iterableVar])
        condition = Expr.Binary(compareLeft, compareToken, compareRight)

        # __UNUSED__VAR = __UNUSED__VAR + 1;
        incrementLHS = Expr.Variable(indexToken)
        dummyOper = Token(TokenType.PLUS, "+", None, 0, 0, "")
        incrementRHS = Expr.Binary(incrementLHS, dummyOper, Expr.Literal(float(1)))
        increment = Expr.Assign(indexToken, colon, incrementRHS)

        # i = array[__UNUSED__VAR];
        nextElement = Expr.Access(iterableVar, colon, Expr.Variable(indexToken), None)
        iterNextElement = Expr.Assign(iterator, colon, nextElement)

        currentLoop = self.loopType
        previousStruct = self.inStructure

        self.inStructure = True
        self.loopType = "forLoop"

        body = self.statement()

        self.loopType = currentLoop
        self.inStructure = previousStruct

        body = Stmt.Block([Stmt.Expression(iterNextElement), body, Stmt.Expression(increment)])
        loop = Stmt.While(condition, body)
        full = Stmt.Block([indexDecl, iteratorDecl, loop])

        self.loopLevel -= 1
        return full

    def forStatement(self) -> Stmt.While | Stmt.Block:
        self.loopLevel += 1
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            if self.peekNext().type == TokenType.COLON:
                return self.rangeForLoop("var")
            initializer = self.varDeclaration("VAR")
        else:
            if self.peekNext().type == TokenType.COLON:
                return self.rangeForLoop("assign")
            initializer = self.expressionStatement()
        
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        # Set the loop type to "forLoop", then reset once the loop body has been parsed.
        currentLoop = self.loopType
        previousStruct = self.inStructure
        
        self.currentStruct = True
        self.loopType = "forLoop"

        body = self.statement()

        self.loopType = currentLoop
        self.inStructure = previousStruct

        if increment != None:
            body = Stmt.Block([body, Stmt.Expression(increment)])
        
        if condition == None:
            condition = Expr.Literal(True)
        body = Stmt.While(condition, body)

        if initializer != None:
            body = Stmt.Block([initializer, body])
        
        self.loopLevel -= 1
        return body
    
    def groupDeclaration(self) -> Stmt.Group:
        groupName = self.consume(TokenType.IDENTIFIER, "Expect group name.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' after group name.")
        vars = []
        functions = []
        classes = []
        while (not self.check(TokenType.RIGHT_BRACE)) and (not self.isAtEnd()):
            blame = self.peek()
            stmt = self.declaration()
            if type(stmt) == Stmt.Class:
                classes.append(stmt)
            elif type(stmt) == Stmt.Var:
                vars.append(stmt)
            elif type(stmt) == Stmt.List:
                vars.append(stmt)
            elif type(stmt) == Stmt.Function:
                functions.append(stmt)
            elif type(stmt) == Stmt.Group:
                vars.append(stmt)
            else:
                raise ParseError(blame, "Invalid group member.")
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after group body.")
        return Stmt.Group(groupName, vars, functions, classes)

    def ifStatement(self) -> Stmt.If:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        previousStruct = self.inStructure
        self.inStructure = True

        thenBranch = self.statement()
        elseBranch = None
        if self.match(TokenType.ELSE):
            self.inStructure = True
            elseBranch = self.statement()

        self.inStructure = previousStruct
        
        return Stmt.If(condition, thenBranch, elseBranch)
    
    def listDeclaration(self) -> Stmt.List:
        name = self.consume(TokenType.IDENTIFIER, "Expect list name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after list declaration.")
            
        return Stmt.List(name, initializer)
    
    def matchStruct(self) -> Stmt.Match:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' before match value.")
        matchValue = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' before match value.")
        cases = []
        default = None
        while self.match(TokenType.IS):
            fallthrough = False
            end = False
            if self.match(TokenType.Q_MARK):
                self.consume(TokenType.COLON, "Expect ':' after case value.")
                stmt = self.declaration()
                default = {
                            "value": None, 
                            "stmt": stmt,
                            "fall": fallthrough,
                            "end": end
                          }
                break
            caseValue = self.expression()
            self.consume(TokenType.COLON, "Expect ':' after case value.")
            caseStmt = self.declaration()
            if self.match(TokenType.FALLTHROUGH):
                if self.match(TokenType.END):
                    raise ParseError(self.previous(),
                                     "Cannot end directly after fallthrough.")
                fallthrough = True
            elif self.match(TokenType.END):
                if self.match(TokenType.FALLTHROUGH):
                    raise ParseError(self.previous(),
                                     "Cannot put 'fallthrough' after 'end'.")
                end = True
            cases.append({
                          "value": caseValue,
                          "stmt": caseStmt,
                          "fall": fallthrough,
                          "end": end
                        })

        return Stmt.Match(matchValue, cases, default)
    
    def printStatement(self) -> Stmt.Print:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)
    
    def reportStatement(self) -> Stmt.Report:
        keyword = self.previous()
        error = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after error report.")
        return Stmt.Report(keyword, error)

    def returnStatement(self) -> Stmt.Return:
        keyword = self.previous()

        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")

        # Report a warning if any code follows a return statement in the same scope.
        if (not self.check(TokenType.RIGHT_BRACE)) and (not self.isAtEnd()):
            if not self.inStructure:
                returnWarning(self.peek()).warn()

        return Stmt.Return(keyword, value)

    def safeDeclaration(self) -> Stmt.Expression:
        keyword = self.previous()
        declaration = self.assignment()
        if type(declaration) != Expr.Set:
            raise ParseError(keyword, 
                               "Cannot use modifier 'safe' outside of field declaration.")
        declaration.access = "private"
        self.consume(TokenType.SEMICOLON, "Expect ';' after private field declaration.")
        return Stmt.Expression(declaration)

    def varDeclaration(self, access) -> Stmt.Var:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        equals = None
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            initializer = self.expression()
        elif access == "FIX":
            raise ParseError(self.peek(), "Must provide initializer to fixed variable.")
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")

        return Stmt.Var(name, equals, initializer, access)
    
    def whileStatement(self) -> Stmt.While:
        self.loopLevel += 1

        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        
        currentLoop = self.loopType
        previousStruct = self.inStructure
        
        self.inStructure = True
        self.loopType = "whileLoop"

        body = self.statement()

        self.loopType = currentLoop
        self.inStructure = previousStruct

        self.loopLevel -= 1
        return Stmt.While(condition, body)
    
    def expressionStatement(self) -> Stmt.Expression:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Expression(expr)
    
    def addParameter(self, parameters: list[Any], defaultFound: bool, 
                        defaults: int, variadic: bool) -> tuple[bool, int, bool]:
        if len(parameters) >= 255:
            raise ParseError(self.peek(), "Can't have more than 255 parameters.")
        if self.match(TokenType.ELLIPSIS):
            if defaultFound:
                raise ParseError(self.previous(),
                    "Can't have variable-length parameter list following default parameter.")
            parameters.append(self.previous())
            variadic = True
            return (defaultFound, defaults, variadic)
        name = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.lambdaExpr()
            parameters.append(Expr.Assign(name, equals, value))
            defaultFound = True
            defaults += 1
        else:
            if defaultFound:
                raise ParseError(name, 
                    "Cannot have regular parameter following default parameter.")
            parameters.append(name)
        return (defaultFound, defaults, variadic)

    def function(self, kind) -> Stmt.Function:
        # Default in case of unassigned lambda.
        funcName = None

        # Check that the function is not an unassigned lambda.
        if kind != "lambda":
            funcName = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")

        prevInit = self.inInit
        self.inInit = (self.inClass and (funcName.lexeme == "init"))

        parameters = None

        defaultFound = False
        defaults = 0
        variadic = False
        # Allow omitting the parameter list entirely in method getters.
        if (kind != "method") or self.check(TokenType.LEFT_PAREN):
            self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
            parameters = list()
            if not self.check(TokenType.RIGHT_PAREN):
                # Implementing do-while logic.
                defaultFound, defaults, variadic = self.addParameter(parameters, 
                                                    defaultFound, defaults, variadic)
                while (self.match(TokenType.COMMA)) and not variadic:
                    defaultFound, defaults, variadic = self.addParameter(parameters, 
                                                        defaultFound, defaults, variadic)
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        # Cannot use f-strings here due to the presence of the { character.
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before " + kind + " body.")
        body = self.block()

        self.inInit = prevInit
        return Stmt.Function(funcName, parameters, body, defaults)
    
    def block(self) -> list[Stmt]:
        statements = list()

        previousStruct = self.inStructure
        self.inStructure = False

        while (not self.check(TokenType.RIGHT_BRACE)) and (not self.isAtEnd()):
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        self.inStructure = previousStruct

        return statements
    
    def expression(self) -> Expr:
        return self.comma()

    def comma(self) -> Expr:
        expressions = list()

        expr = self.lambdaExpr()
        expressions.append(expr)

        while self.match(TokenType.COMMA):
            expr = self.lambdaExpr()
            expressions.append(expr)
        
        if len(expressions) > 1:
            return Expr.Comma(expressions)
        
        return expr
    
    # Lambda implementation my own.
    # Lambda expressions create name-less functions.
    # Called lambdaExpr since lambda is a keyword.
    '''
    Made it an expression since a lambda is supposed to be an evaluated value parameter
    in a function or operation (it is passed as a value, not "run" as a statement) and 
    since its visit method returns an expression, and it would be unwise to mix 
    statement classes and expression-returning visit methods.
    '''
    def lambdaExpr(self) -> Expr:
        if self.match(TokenType.FUN):
            self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'fun' keyword.")

            parameters = list()
            defaultFound = False
            defaults = 0
            variadic = False
            if not self.check(TokenType.RIGHT_PAREN):
                # Implementing do-while logic.
                defaultFound, defaults, variadic = self.addParameter(parameters, 
                                                    defaultFound, defaults, variadic)
                while self.match(TokenType.COMMA):
                    defaultFound, defaults, variadic = self.addParameter(parameters, 
                                                    defaultFound, defaults, variadic)
            
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
            self.consume(TokenType.LEFT_BRACE, "Expect '{' before lambda body.")
            body = self.block()

            return Expr.Lambda(parameters, body, defaults)
        
        return self.assignment()
    
    def assignment(self) -> Expr:
        # For +=, -=, *=, and /= operators.
        validTypes = (TokenType.PLUS_EQUALS,
                       TokenType.MINUS_EQUALS,
                       TokenType.STAR_EQUALS,
                       TokenType.SLASH_EQUALS,
                       TokenType.POST_INC,
                       TokenType.POST_DEC)

        expr = self.orExpr()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.lambdaExpr()

            if type(expr) == Expr.Variable:
                name = expr.name
                return Expr.Assign(name, equals, value)
            
            if type(expr) == Expr.Get:
                return Expr.Set(expr.object, expr.name, value, "public")
            
            if type(expr) == Expr.Access:
                return Expr.Modify(expr, equals, value)
            
            raise ParseError(equals, "Invalid assignment target.")

        else:
            for operType in validTypes:
                if self.match(operType):
                    operator = self.previous()
                    binaryOper = self.advance()
                    value = Expr.Literal(float(1))
                    if ((operType != TokenType.POST_INC) and
                        (operType != TokenType.POST_DEC)):
                        value = self.lambdaExpr()

                    rhs = Expr.Binary(expr, binaryOper, value)

                    if type(expr) == Expr.Variable:
                        name = expr.name
                        return Expr.Assign(name, operator, rhs)
                    
                    if type(expr) == Expr.Get:
                        return Expr.Set(expr.object, expr.name, rhs)
                    
                    if type(expr) == Expr.Access:
                        return Expr.Modify(expr, operator, rhs)
                    
                    raise ParseError(operator, "Invalid increment target.")
        
        return expr
    
    def orExpr(self) -> Expr:
        expr = self.andExpr()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.andExpr()
            expr = Expr.Logical(expr, operator, right)
        
        return expr
    
    def andExpr(self) -> Expr:
        expr = self.ternary()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right)
        
        return expr
    
    # Ternary implementation my own.
    def ternary(self) -> Expr:
        expr = self.equality()

        while self.match(TokenType.Q_MARK):
            left = self.expression()
            self.consume(TokenType.COLON,
                        "Expect colon separator between ternary operator branches.")
            right = self.ternary()
            expr = Expr.Ternary(expr, left, right)
        
        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, 
                         TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def factor(self) -> Expr:
        expr = self.unary()

        # Added the modulus operator (same precedence as * and /).
        while self.match(TokenType.SLASH, TokenType.STAR, TokenType.MOD):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)
        
        return self.exponent()
    
    def exponent(self) -> Expr:
        expr = self.call()

        while self.match(TokenType.POWER):
            operator = self.previous()
            # Exponent operator is right-associative.
            right = self.exponent()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def finishCall(self, callee) -> Expr.Call:
        arguments = list()

        leftParen = self.previous()

        if not self.check(TokenType.RIGHT_PAREN):
            if len(arguments) > 255:
                raise ParseError(self.peek(), "Can't have more than 255 arguments.")
            arguments.append(self.lambdaExpr())

            while self.match(TokenType.COMMA):
                if len(arguments) > 255:
                    raise ParseError(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.lambdaExpr())
        
        rightParen = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Expr.Call(callee, leftParen, rightParen, arguments)
    
    def call(self) -> Expr:
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Expr.Get(expr, name)
            elif self.match(TokenType.LEFT_BRACKET):
                start = self.expression()
                end = None
                if self.match(TokenType.DOTDOT):
                    end = self.expression()
                operator = self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after index.")
                expr = Expr.Access(expr, operator, start, end)
            else:
                break
        
        return expr
    
    def listExpr(self) -> Expr.List | None:
        if self.match(TokenType.LEFT_BRACKET):
            operator = self.previous()
            elements = []
            if not self.check(TokenType.RIGHT_BRACKET):
                #element = self.listExpr()
                element = self.lambdaExpr()
                elements.append(element)

                while self.match(TokenType.COMMA):
                    #element = self.listExpr()
                    element = self.lambdaExpr()
                    elements.append(element)
            
            self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after list elements.")
            return Expr.List(elements, operator)
    
    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Expr.Literal(False)
        if self.match(TokenType.TRUE):
            return Expr.Literal(True)
        if self.match(TokenType.NIL):
            return Expr.Literal(None)
        
        if self.match(TokenType.NUMBER):
            return Expr.Literal(self.previous().literal)
        
        if self.match(TokenType.STRING):
            return Expr.Literal(String(self.previous().literal))
        
        if self.match(TokenType.SUPER):
            keyword = self.previous()
            self.consume(TokenType.DOT, 
                         "Expect '.' after 'super'.")
            method = self.consume(TokenType.IDENTIFIER, 
                                  "Expect superclass method name.")
            return Expr.Super(keyword, method)
        
        if self.match(TokenType.THIS):
            return Expr.This(self.previous())
        
        if self.match(TokenType.IDENTIFIER):
            return Expr.Variable(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Expr.Grouping(expr)
        
        if self.check(TokenType.LEFT_BRACKET):
            expr = self.listExpr()
            if type(expr) == Expr.List:
                return Expr.List(expr.elements, expr.operator)
        
        # Could possibly add more operators (comma, ternary, etc.), 
        # but these are sufficient as important binary operators.
        # For other operators, the "Expect expression" error message 
        # would probably be sufficient.
        # Slash could not be used here at the beginning for a comment, 
        # as comments are eliminated in the scanning stage.
        operators = (TokenType.PLUS, TokenType.MINUS, TokenType.STAR, 
                     TokenType.SLASH, TokenType.MOD, TokenType.POWER,
                     TokenType.AND, TokenType.OR)
        for x in operators:
            if self.match(x):
                raise ParseError(self.previous(), "Missing left operand.")
        
        raise ParseError(self.peek(), "Expect expression.")

    def match(self, *args) -> bool: # *args: variable number of non-keyword arguments.
        for type in args:
            if self.check(type):
                self.advance()
                return True
        
        return False

    def consume(self, type: TokenType, message: str) -> Token | None:
        if self.check(type):
            return self.advance()
        # Put error code here instead.
        raise ParseError(self.peek(), message)

    def check(self, type: TokenType) -> bool:
        if self.isAtEnd():
            return False
        return (self.peek().type == type)

    def advance(self) -> Token:
        if not self.isAtEnd():
            self.current += 1
        return self.previous()        

    def isAtEnd(self) -> bool:
        return (self.peek().type == TokenType.EOF)

    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def peekNext(self) -> Token:
        return self.tokens[self.current + 1]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def synchronize(self) -> None:
        self.advance()

        while not self.isAtEnd():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            match self.peek().type:
                case TokenType.CLASS:
                    return
                case TokenType.FUN:
                    return
                case TokenType.VAR:
                    return
                case TokenType.FOR:
                    return
                case TokenType.IF:
                    return
                case TokenType.WHILE:
                    return
                case TokenType.PRINT:
                    return
                case TokenType.RETURN:
                    return
            
            self.advance()