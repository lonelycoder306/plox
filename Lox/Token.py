from enum import Enum

TokenType = Enum('TokenType', 
                 'LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE, LEFT_BRACKET, RIGHT_BRACKET, ' 
                 'COMMA, DOT, DOTDOT, MINUS, PLUS, SEMICOLON, SLASH, STAR, ' 
                 'BANG, BANG_EQUAL, EQUAL, EQUAL_EQUAL, GREATER, GREATER_EQUAL, LESS, LESS_EQUAL, ' 
                 'IDENTIFIER, STRING, NUMBER, AND, CLASS, ELSE, FALSE, FUN, FOR, IF, ' 
                 'NIL, OR, PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE, EOF, ' 
                 'BREAK, CONTINUE, Q_MARK, COLON, MOD, POWER, LIST, GET, '
                 'SAFE, ATTEMPT, HANDLE, REPORT, ELLIPSIS, PLUS_EQUALS,'
                 'MINUS_EQUALS, STAR_EQUALS, SLASH_EQUALS')

class Token:
    def __init__(self, type: TokenType, lexeme: str, literal, line: int, column: int, fileName: str):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.column = column
        self.fileName = fileName
    
    def toString(self):
        if self.type.name != "EOF":
            return self.type.name + " " + self.lexeme + " " + str(self.literal)
        return self.type.name + " Null"