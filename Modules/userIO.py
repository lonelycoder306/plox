from Lox.Environment import Environment
from Lox.LoxCallable import LoxCallable
from Lox.Error import RuntimeError
from Lox.List import List
from Lox.String import String
import sys

userIO = Environment()
functions = ["inchars", "inbytes", "inline", "inlines", "inpeek", "echo"]

class IOFunction(LoxCallable):
    def __init__(self, mode: str):
        self.mode = mode
    
    def call(self, interpreter, expr, arguments):
        match self.mode:
            case "inchars":
                if not self.check_inchars(arguments):
                    raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number, boolean.")
                # Our numbers are all saved as floats, but read() only accepts integers.
                if len(arguments) == 2:
                    return self.io_inchars(int(arguments[0]), arguments[1])
                elif len(arguments) == 1:
                    return self.io_inchars(int(arguments[0]))
            case "inbytes":
                if not self.check_inbytes(arguments):
                    raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number.")
                if len(arguments) == 2:
                    return self.io_inbytes(int(arguments[0]), arguments[1])
                elif len(arguments) == 1:
                    return self.io_inbytes(int(arguments[0]))
            case "inline":
                if not self.check_inline(arguments):
                    raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.")
                return self.io_inline()
            case "inlines":
                if not self.check_inlines(arguments):
                    raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number.")
                return self.io_inlines(int(arguments[0]))
            case "inpeek":
                if not self.check_inpeek(arguments):
                    raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.")
                return self.io_inpeek()
            case "echo":
                if not self.check_echo(arguments):
                    raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: string.")
                self.io_echo(arguments[0])
                return ()
    
    def arity(self):
        match self.mode:
            case "inchars":
                return [1,2]
            case "inbytes":
                return [1,2]
            case "inline":
                return [0,0]
            case "inlines":
                return [0,1]
            case "inpeek":
                return [0,0]
            case "echo":
                return [1,1]
    
    # Input.

    def io_inchars(self, n: int, delim: bool = False):
        if delim:
            string = ""
            char = ""
            while True:
                char = sys.stdin.read(1)
                if char == '\n':
                    break
                string += char
            return String(string)
        else:
            return String(sys.stdin.read(n))

    def io_inbytes(self, n: int, delim: bool = False):
        if delim:
            string = b""
            char = b""
            while True:
                char = sys.stdin.buffer.read(1)
                if (char == b'\n') or (char == b'\r'):
                    break
                string += char
            return string
        else:
            return sys.stdin.buffer.read(n)
    
    def io_inline(self):
        string = sys.stdin.readline()
        if string[-1] == '\n':
            return String(string[:-1])
        return String(string)
    
    def io_inlines(self, n: int = -1):
        if n != -1:
            lineList = []
            for i in range(0, n):
                lineList.append(sys.stdin.readline())
        else:
            lineList = sys.stdin.readlines()
        lineList = [String(line.rstrip('\n')) for line in lineList]
        return List(lineList)

    def io_inpeek(self):
        return String(sys.stdin.read(1))
    
    # Output.

    def io_echo(self, arg: String):
        printText = arg.text.encode("utf-8").decode("unicode_escape")
        print(printText)
    
    # Error checking.

    def check_inchars(self, arguments):
        # No need for argument number checks since that is already a part of the interpreter.
        if (type(arguments[0]) == float):
            if (len(arguments) == 1) or (type(arguments[1]) == bool):
                return True
        return False
    
    def check_inbytes(self, arguments):
        if type(arguments[0]) == float:
            return True
        return False
    
    def check_inline(self, arguments):
        return True

    def check_inlines(self, arguments):
        if len(arguments) or type(arguments[0]) == float:
            return True
        return False
    
    def check_inpeek(self, argument):
        return True

    def check_echo(self, arguments):
        if type(arguments[0]) == str:
            return True
        return False
    
    def toString(self):
        return "<userIO function>"
    
def userIOSetUp():
    for function in functions:
        userIO.define(function, IOFunction(function))