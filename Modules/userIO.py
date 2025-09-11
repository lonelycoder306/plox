import os
import sys
sys.path.append(os.getcwd() +  "/Lox")
from importlib import import_module as im
Environment = getattr(im("Environment"), "Environment")
LoxCallable = getattr(im("LoxCallable"), "LoxCallable")
RuntimeError = getattr(im("Error"), "RuntimeError")
List = getattr(im("List"), "List")
String = getattr(im("String"), "String")

userIO = Environment()
functions = ["inchars", "inbytes", "inword", "inline", "inlines", "inpeek", "echo", "inflush", "outflush"]

class IOFunction(LoxCallable):
    def __init__(self, mode: str):
        self.mode = mode
    
    def check(self, expr, arguments):
        funcString = "check_" + self.mode
        func = IOFunction.__dict__[funcString]
        return func(self, expr, arguments)
    
    def call(self, interpreter, expr, arguments):
        if self.check(expr, arguments):
            match self.mode:
                case "inchars":
                    # Our numbers are all saved as floats, but read() only accepts integers.
                    if len(arguments) == 2:
                        return self.io_inchars(int(arguments[0]), arguments[1])
                    elif len(arguments) == 1:
                        return self.io_inchars(int(arguments[0]))
                case "inbytes":
                    if len(arguments) == 2:
                        return self.io_inbytes(int(arguments[0]), arguments[1])
                    elif len(arguments) == 1:
                        return self.io_inbytes(int(arguments[0]))
                case "inword":
                    return self.io_inword()
                case "inline":
                    return self.io_inline()
                case "inlines":
                    return self.io_inlines(int(arguments[0]))
                case "inpeek":
                    return self.io_inpeek()
                case "echo":
                    self.io_echo(arguments[0], expr)
                    return ()
                case "inflush":
                    self.io_inflush()
                    return ()
                case "outflush":
                    self.io_outflush()
                    return ()
    
    def arity(self):
        match self.mode:
            case "inchars":
                return [1,2]
            case "inbytes":
                return [1,2]
            case "inword":
                return [0,0]
            case "inline":
                return [0,0]
            case "inlines":
                return [0,1]
            case "inpeek":
                return [0,0]
            case "echo":
                return [1,1]
            case "inflush":
                return [0,0]
            case "outflush":
                return [0,0]
    
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

    def io_inword(self):
        string = ""
        char = ""
        while True:
            char = sys.stdin.read(1)
            if char.isspace():
                break
            string += char
        return String(string)

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

    def io_echo(self, arg, expr):
        try:
            printText = arg.text.encode("utf-8").decode("unicode_escape")
            print(printText)
        except UnicodeDecodeError:
            raise RuntimeError(expr.leftParen, "Failed to format string.")
    
    # Buffer flushing.

    def io_inflush(self):
        import os
        if os.name == "nt": # Using Windows.
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        else: # POSIX.
            # Cannot import termios at the beginning since 
            # it doesn't work on Windows.
            import termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
    
    def io_outflush(self):
        sys.stdout.flush()
    
    # Error checking.

    def check_inchars(self, expr, arguments):
        # No need for argument number checks since that is already a part of the interpreter.
        if (type(arguments[0]) == float):
            if (len(arguments) == 1) or (type(arguments[1]) == bool):
                return True
        raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number, boolean.")
    
    def check_inbytes(self, expr, arguments):
        if type(arguments[0]) == float:
            return True
        raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number.")

    def check_inword(self, expr, arguments):
        return True
    
    def check_inline(self, expr, arguments):
        return True

    def check_inlines(self, expr, arguments):
        if len(arguments) or type(arguments[0]) == float:
            return True
        raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number.")
    
    def check_inpeek(self, expr, arguments):
        return True

    def check_echo(self, expr, arguments):
        if type(arguments[0]) == String:
            return True
        raise RuntimeError(expr.rightParen, 
                                       "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number.")

    def check_inflush(self, expr, arguments):
        return True
    
    def check_outflush(self, expr, arguments):
        return True
    
    def toString(self):
        return "<userIO function>"
    
def userIOSetUp():
    for function in functions:
        userIO.define(function, IOFunction(function))