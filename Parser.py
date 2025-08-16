from Token import TokenType, Token
from Expr import Expr
from Stmt import Stmt
from Error import ParseError
from Warning import returnWarning

class Parser:
    tokens = list()
    current = 0

    def __init__(self, tokens):
        self.tokens = tokens
        # Will be None when not in a loop, "forLoop" when within a for-loop, 
        # and "whileLoop" when within a while-loop.
        self.loopType = None
        self.loopLevel = 0
    
    def parse(self):
        statements = list()
        while not self.isAtEnd():
            try:
                statements.append(self.declaration())
            except ParseError as error:
                self.synchronize()
                error.show()
        
        return statements
    
    def declaration(self):
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
            return self.varDeclaration()
        
        if self.match(TokenType.LIST):
            return self.listDeclaration()
        
        return self.statement()
            
    def statement(self):
        if self.match(TokenType.BREAK):
            return self.breakStatement()
        if self.match(TokenType.CONTINUE):
            return self.continueStatement()
        if self.match(TokenType.FOR):
            return self.forStatement()
        if self.match(TokenType.IF):
            return self.ifStatement()
        if self.match(TokenType.PRINT):
            return self.printStatement()
        if self.match(TokenType.RETURN):
            return self.returnStatement()
        if self.match(TokenType.WHILE):
            return self.whileStatement()
        if self.match(TokenType.LEFT_BRACE):
            return Stmt.Block(self.block())
        if self.match(TokenType.GET):
            return self.fetchStatement()

        return self.expressionStatement()

    def breakStatement(self):
        breakToken = self.previous()
        if self.loopLevel == 0:
            raise ParseError(breakToken, "Cannot have 'break' outside loop.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return Stmt.Break(breakToken, self.loopType)
    
    def classDeclaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = list()
        while (not self.check(TokenType.RIGHT_BRACE)) and (not self.isAtEnd()):
            methods.append(self.function("method"))

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return Stmt.Class(name, methods)

    def continueStatement(self):
        continueToken = self.previous()
        if self.loopLevel == 0:
            raise ParseError(continueToken, "Cannot have 'continue' outside loop.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return Stmt.Continue(continueToken, self.loopType)
    
    def fetchStatement(self):
        mode = self.previous()
        name = None
        if (mode.lexeme[3:] == "Lib"):
            name = self.consume(TokenType.STRING, "Expect name of import.")
            self.consume(TokenType.SEMICOLON, "Expect ';' after fetch statement.")

            from Scanner import Scanner
            file = "Libraries/" + name.lexeme[1:-1]
            try:
                with open(file, "r") as f:
                    text = f.read()
                f.close()
                import State
                with open(file, "r") as f:
                    State.fileLines[file] = f.readlines()
            except FileNotFoundError:
                raise ParseError(name, "No such library file.")
            scanner = Scanner(text, file)
            newTokens = scanner.scanTokens()[:-1]
            self.tokens[self.current:self.current] = newTokens

        elif (mode.lexeme[3:] == "File"):
            name = self.consume(TokenType.STRING, "Expect name of import.")
            self.consume(TokenType.SEMICOLON, "Expect ';' after fetch statement.")

            from Scanner import Scanner
            file = name.lexeme[1:-1]
            try:
                text = open(file, "r").read()
            except FileNotFoundError:
                raise ParseError(name, "File not found.")
            scanner = Scanner(text)
            newTokens = scanner.scanTokens()[:-1]
            self.tokens[self.current:self.current] = newTokens

        elif mode.lexeme[3:] == "Mod":
            name = self.consume(TokenType.STRING, "Expect name of import.")
            self.consume(TokenType.SEMICOLON, "Expect ';' after fetch statement.")

        return Stmt.Fetch(mode, name)

    def forStatement(self):
        self.loopLevel += 1
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.varDeclaration()
        else:
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
        self.loopType = "forLoop"
        body = self.statement()
        self.loopType = currentLoop

        if increment != None:
            body = Stmt.Block([body, Stmt.Expression(increment)])
        
        if condition == None:
            condition = Expr.Literal(True)
        body = Stmt.While(condition, body)

        if initializer != None:
            body = Stmt.Block([initializer, body])
        
        self.loopLevel -= 1
        return body

    def ifStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        thenBranch = self.statement()
        elseBranch = None
        if self.match(TokenType.ELSE):
            elseBranch = self.statement()
        
        return Stmt.If(condition, thenBranch, elseBranch)
    
    def listDeclaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect list name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after list declaration.")
            
        return Stmt.List(name, initializer)
    
    def printStatement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)
    
    def returnStatement(self):
        keyword = self.previous()

        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")

        # Report a warning if any code follows a return statement in the same scope.
        if (not self.check(TokenType.RIGHT_BRACE)) and (not self.isAtEnd()):
            returnWarning(self.peek()).warn()

        return Stmt.Return(keyword, value)

    def varDeclaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)
    
    def whileStatement(self):
        self.loopLevel += 1

        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        currentLoop = self.loopType
        self.loopType = "whileLoop"
        body = self.statement()
        self.loopType = currentLoop

        self.loopLevel -= 1
        return Stmt.While(condition, body)
    
    def expressionStatement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Expression(expr)
    
    def function(self, kind):
        # Default in case of unassigned lambda.
        name = None

        # Check that the function is not an unassigned lambda.
        if kind != "lambda":
            name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        parameters = list()
        if not self.check(TokenType.RIGHT_PAREN):
            # Implementing do-while logic.
            if len(parameters) >= 255:
                raise ParseError(self.peek(), "Can't have more than 255 parameters.")
            parameters.append(self.consume(TokenType.IDENTIFIER,
                        "Expect parameter name."))
            
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    raise ParseError(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER,
                            "Expect parameter name."))
            
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        # Cannot use f-strings here due to the presence of the { character.
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before " + kind + " body.")
        body = self.block()
        return Stmt.Function(name, parameters, body)
    
    def block(self):
        statements = list()

        while (not self.check(TokenType.RIGHT_BRACE)) and (not self.isAtEnd()):
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def expression(self):
        return self.comma()

    def comma(self):
        expressions = list()

        expr = self.listExpr()
        expressions.append(expr)

        while self.match(TokenType.COMMA):
            expr = self.listExpr()
            expressions.append(expr)
        
        if len(expressions) > 1:
            return Expr.Comma(expressions)
        
        return expr
    
    def listExpr(self):
        if self.match(TokenType.LEFT_BRACKET):
            operator = self.previous()
            elements = []
            if not self.check(TokenType.RIGHT_BRACKET):
                element = self.listExpr()
                elements.append(element)

                while self.match(TokenType.COMMA):
                    element = self.listExpr()
                    elements.append(element)
            
            self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after list elements.")
            return Expr.List(elements, operator)
        
        return self.lambdaExpr()
    
    # Lambda implementation my own.
    # Lambda expressions create name-less functions.
    # Called lambdaExpr since lambda is a keyword.
    '''
    Made it an expression since a lambda is supposed to be an evaluated value parameter
    in a function or operation (it is passed as a value, not "run" as a statement) and 
    since its visit method returns an expression, and it would be unwise to mix 
    statement classes and expression-returning visit methods.
    '''
    def lambdaExpr(self):
        if self.match(TokenType.FUN):
            self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'fun' keyword.")

            parameters = list()
            if not self.check(TokenType.RIGHT_PAREN):
                if len(parameters) >= 255:
                    raise ParseError(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER,
                            "Expect parameter name."))
                
                while self.match(TokenType.COMMA):
                    if len(parameters) >= 255:
                        raise ParseError(self.peek(), "Can't have more than 255 parameters.")
                    parameters.append(self.consume(TokenType.IDENTIFIER,
                                "Expect parameter name."))
            
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

            self.consume(TokenType.LEFT_BRACE, "Expect '{' before lambda body.")
            body = self.block()

            return Expr.Lambda(parameters, body)
        
        return self.assignment()
    
    def assignment(self):
        expr = self.orExpr()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.listExpr()

            if type(expr) == Expr.Variable:
                name = expr.name
                return Expr.Assign(name, value)
            
            if type(expr) == Expr.Get:
                return Expr.Set(expr.object, expr.name, value)
            
            if (type(expr) == Expr.Access) and (type(expr.object) == Expr.Variable):
                return Expr.Modify(expr, value)
            
            raise ParseError(equals, "Invalid assignment target.")
        
        return expr
    
    def orExpr(self):
        expr = self.andExpr()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.andExpr()
            expr = Expr.Logical(expr, operator, right)
        
        return expr
    
    def andExpr(self):
        expr = self.ternary()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right)
        
        return expr
    
    # Ternary implementation my own.
    def ternary(self):
        expr = self.equality()

        while self.match(TokenType.Q_MARK):
            left = self.equality()
            self.consume(TokenType.COLON,
                        "Expect colon separator between ternary operator branches.")
            right = self.ternary()
            expr = Expr.Ternary(expr, left, right)
        
        return expr

    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def comparison(self):
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, 
                         TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def term(self):
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def factor(self):
        expr = self.unary()

        # Added the modulus operator (same precedence as * and /).
        while self.match(TokenType.SLASH, TokenType.STAR, TokenType.MOD):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)
        
        return self.exponent()
    
    def exponent(self):
        expr = self.call()

        while self.match(TokenType.POWER):
            operator = self.previous()
            # Exponent operator is right-associative.
            right = self.exponent()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def finishCall(self, callee):
        arguments = list()

        if not self.check(TokenType.RIGHT_PAREN):
            if len(arguments) > 255:
                raise ParseError(self.peek(), "Can't have more than 255 arguments.")
            arguments.append(self.listExpr())

            while self.match(TokenType.COMMA):
                if len(arguments) > 255:
                    raise ParseError(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.listExpr())
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Expr.Call(callee, paren, arguments)
    
    def call(self):
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Expr.Get(expr, name)
            elif self.match(TokenType.LEFT_BRACKET):
                start = self.assignment()
                end = None
                if self.match(TokenType.DOTDOT):
                    end = self.assignment()
                operator = self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after index.")
                expr = Expr.Access(expr, operator, start, end)
            else:
                break
        
        return expr
    
    def primary(self):
        if self.match(TokenType.FALSE):
            return Expr.Literal(False)
        if self.match(TokenType.TRUE):
            return Expr.Literal(True)
        if self.match(TokenType.NIL):
            return Expr.Literal(None)
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal)
        
        if self.match(TokenType.THIS):
            return Expr.This(self.previous())
        
        if self.match(TokenType.IDENTIFIER):
            return Expr.Variable(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Expr.Grouping(expr)
        
        # Could possibly add more operators (comma, ternary, etc.), but these are sufficient as important binary operators.
        # For other operators, the "Expect expression" error message would probably be sufficient.
        # Slash could not be used here at the beginning for a comment, as comments are eliminated in the scanning stage.
        operators = (TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.MOD, TokenType.POWER,
                    TokenType.AND, TokenType.OR)
        for x in operators:
            if self.match(x):
                raise ParseError(self.previous(), "Missing left operand.")
        
        raise ParseError(self.peek(), "Expect expression.")

    def match(self, *args): # *args: variable number of non-keyword arguments
        for type in args:
            if self.check(type):
                self.advance()
                return True
        
        return False

    def consume(self, type: TokenType, message: str):
        if self.check(type):
            return self.advance()
        # Put error code here instead.
        raise ParseError(self.peek(), message)

    def check(self, type: TokenType):
        if self.isAtEnd():
            return False
        return (self.peek().type == type)

    def advance(self):
        if not self.isAtEnd():
            self.current += 1
        return self.previous()        

    def isAtEnd(self) -> bool:
        return (self.peek().type == TokenType.EOF)

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def synchronize(self):
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