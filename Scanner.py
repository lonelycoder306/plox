from Token import Token, TokenType
from Error import LexError

class Scanner:
    source = str()
    tokens = list()
    fileName = str()
    start = 0
    current = 0
    column = 0 # First character on line is at column 1 (advance increments column immediately upon the first character).
    line = 1

    keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
        "break": TokenType.BREAK,
        "continue": TokenType.CONTINUE,
        "list": TokenType.LIST,
        "GetMod": TokenType.GET,
        "GetLib": TokenType.GET,
        "GetFile": TokenType.GET
    }

    def __init__(self, source, fileName):
        self.source = source
        self.fileName = fileName

    def scanTokens(self):
        # Reset the list to be empty so that it is ready for each new line/file.
        self.tokens = []
        while not self.isAtEnd():
            # We are at the beginning of the next lexeme.
            self.start = self.current
            try:
                self.scanToken()
            except LexError as error:
                error.show()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line, self.column, self.fileName))
        return self.tokens

    def scanToken(self):
        c = self.advance()
        self.column += 1

        match c:
            case '(':
                self.addToken(TokenType.LEFT_PAREN)
            case ')':
                self.addToken(TokenType.RIGHT_PAREN)
            case '{':
                self.addToken(TokenType.LEFT_BRACE)
            case '}':
                self.addToken(TokenType.RIGHT_BRACE)
            case '[':
                self.addToken(TokenType.LEFT_BRACKET)
            case ']':
                self.addToken(TokenType.RIGHT_BRACKET)
            case ',':
                self.addToken(TokenType.COMMA)
            case '.':
                if self.match('.'):
                    self.addToken(TokenType.DOTDOT)
                else:
                    self.addToken(TokenType.DOT)
            case '-':
                if self.match('-'):
                    self.addToken(TokenType.PRE_DEC)
                self.addToken(TokenType.MINUS)
            case '+':
                if self.match('+'):
                    self.addToken(TokenType.PRE_INC)
                self.addToken(TokenType.PLUS)
            case ';':
                self.addToken(TokenType.SEMICOLON)
            case '*':
                self.addToken(TokenType.STAR)
            case '?':
                self.addToken(TokenType.Q_MARK)
            case ':':
                self.addToken(TokenType.COLON)
            # Two personal additions.
            case '%':
                self.addToken(TokenType.MOD)
            case '^':
                self.addToken(TokenType.POWER)
            
            case '!':
                self.addToken(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=':
                self.addToken(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<':
                self.addToken(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>':
                self.addToken(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            
            case '/':
                if self.match('/'):
                    # A comment goes until the end of the line.
                    while self.peek() != '\n' and (not self.isAtEnd()):
                        self.advance()
                
                # Own implementation for comment blocks (including nesting).
                elif self.match('*'):
                    count = 1
                    while count != 0 and (not self.isAtEnd()):
                        # Newlines: increment line and skip a character.
                        if self.peek() == '\n':
                            self.line += 1
                        elif self.peek() == '/' and self.peekNext() == '*':
                            count += 1
                            # Skip two characters (combined with advance outside if-else-if block).
                            self.advance()
                        elif self.peek() == '*' and self.peekNext() == '/':
                            count -= 1
                            self.advance()
                        self.advance() # Avoids adding an extra advance() in each block.
                    if count != 0:
                        raise LexError(self.line, self.column, self.fileName, "Unterminated comment block.")
                
                else:
                    self.addToken(TokenType.SLASH)
            
            # Ignore whitespace.
            case ' ':
                # No fall-through behavior.
                pass
            case '\r':
                pass
            case '\t':
                pass
            
            case '\n':
                self.line += 1
                self.column = 0
            
            case '"':
                self.string()
            
            case _:
                if c.isdigit():
                    self.number()
                elif c.isalpha() or c == '_':
                    self.identifier()
                else:
                    raise LexError(self.line, self.column, self.fileName, "Unexpected character.")
    
    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        
        text = self.source[self.start:self.current]
        # Make type IDENTIFIER if text not found in keywords.
        type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.addToken(type)
        # Increment the column counter to skip the token.
        # Only increment after the token is added to not change the starting position saved with the token.
        # -1 to only make it move to the end of the token, not beyond it (it is already on the first character of the token).
        self.column += len(self.tokens[-1].lexeme) - 1
    
    def number(self):
        while self.peek().isdigit():
            self.advance()
        # Look for a fractional part.
        if (self.peek() == '.' and self.peekNext().isdigit()):
            # Consume the ".".
            self.advance()
            while self.peek().isdigit():
                self.advance()
        self.addToken(TokenType.NUMBER, float(self.source[self.start:self.current]))
        self.column += len(self.tokens[-1].lexeme) - 1
    
    def string(self):
        while (self.peek() != '"') and (not self.isAtEnd()):
            if self.peek() == '\n':
                self.line += 1
                self.column = 0
            self.advance()
        if self.isAtEnd():
            raise LexError(self.line, self.column, self.fileName, "Unterminated string.")
        # The closing ".
        self.advance()
        
        # Trim the surrounding quotes.
        value = self.source[self.start + 1:self.current - 1]
        self.addToken(TokenType.STRING, value)
        self.column += len(self.tokens[-1].lexeme) - 1
    
    def match(self, expected):
        if self.isAtEnd():
            return False
        if self.source[self.current] != expected:
            return False
        self.current = self.current + 1
        return True
    
    def peek(self):
        if self.isAtEnd():
            return ""
        return self.source[self.current]
    
    def peekNext(self):
        if (self.current + 1 >= len(self.source)):
            return ""
        return self.source[self.current + 1]

    def isAtEnd(self):
        return self.current >= len(self.source)
    
    def advance(self):
        self.current += 1
        return self.source[self.current - 1]
    
    # Combined both functions into one to avoid overloading.
    # Used default parameter values instead.
    def addToken(self, type, literal = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line, self.column, self.fileName))