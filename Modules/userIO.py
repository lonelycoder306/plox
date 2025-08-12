from Environment import Environment
from LoxCallable import LoxCallable
from Error import RuntimeError
import sys

userIO = Environment()
functions = ["inchars", "inbytes", "inline", "inlines", "inpeek", "echo"]

class IOFunction(LoxCallable):
    def __init__(self, mode: str):
        self.mode = self.mode = mode
    
    def call(self, interpreter, expr, arguments):
        match self.mode:
            case "inchars":
                if not self.check_inchars(arguments):
                    raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                                        "Types are: number, boolean.")
                return self.io_inchars(int(arguments[0]), arguments[1]) # Our numbers are all saved as floats, but read() only accepts integers.
            case "inbytes":
                if not self.check_inbytes(arguments):
                    raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                                        "Types are: number.")
                return self.io_inbytes(int(arguments[0]))
            case "inline":
                if not self.check_inline(arguments):
                    raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.")
                return self.io_inline()
            case "inlines":
                if not self.check_inlines(arguments):
                    raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                                        "Types are: number.")
                return self.io_inlines(int(arguments[0]))
            case "inpeek":
                if not self.check_inpeek(arguments):
                    raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.")
                return self.io_inpeek()
            case "echo":
                if not self.check_echo(arguments):
                    raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                                        "Types are: string.")
                self.io_echo(arguments[0])
    
    def arity(self):
        match self.mode:
            case "inchars":
                return 2
            case "inbytes":
                return 1
            case "inline":
                return 0
            case "inlines":
                return 1
            case "inpeek":
                return 0
            case "echo":
                return 1
    
    # Input.

    def io_inchars(self, n: int, delim = False):
        if delim:
            string = ""
            char = ""
            while True:
                char = sys.stdin.read(1)
                if char == '\n':
                    break
                string += char
            return string
        else:
            return sys.stdin.read(n)

    def io_inbytes(self, n: int):
        return sys.stdin.buffer.read(n)
    
    def io_inline(self):
        string = sys.stdin.readline()
        if string[-1] == '\n':
            return string[:-1]
        return string
    
    def io_inlines(self, n: int):
        return sys.stdin.readlines(n)

    def io_inpeek(self):
        return sys.stdin.read(1)
    
    # Output.

    def io_echo(self, text: str):
        printText = text.encode("utf-8").decode("unicode_escape")
        print(printText)
    
    # Error checking.

    def check_inchars(self, arguments):
        # No need for argument number checks since that is already a part of the interpreter.
        if (type(arguments[0]) == float) and (type(arguments[1]) == bool):
            return True
        return False
    
    def check_inbytes(self, arguments):
        if type(arguments[0]) == float:
            return True
        return False
    
    def check_inline(self, arguments):
        return True

    def check_inlines(self, arguments):
        if type(arguments[0]) == float:
            return True
        return False
    
    def check_inpeek(self, argument):
        return True

    def check_echo(self, arguments):
        if type(arguments[0]) == str:
            return True
        return False
    
def userIOSetUp():
    for function in functions:
        userIO.define(function, IOFunction(function))