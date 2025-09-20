import sys
from Token import TokenType
from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from Resolver import Resolver
from Error import BaseError, ScanError, ParseError, StaticError, RuntimeError

fileName = None
testMode = False
cleanMode = False
Error = False # True if "-error" or "-linepos" options have been used.
linePos = False # True if line-position info should be printed.
linePrint = False # True if error lines should be printed.
if len(sys.argv) == 2:
    if sys.argv[1] == "-test":
        testMode = True
    if sys.argv[1] == "-clean":
        cleanMode = True
    if sys.argv[1] == "-linepos":
        Error = True
        linePos = True
    if sys.argv[1] == "-error":
        Error = True
        linePos = True
        linePrint = True
    else:
        fileName = sys.argv[1]

interpreter = Interpreter()

def run(source, fileName = "_REPL_"):
    import State

    scanner = Scanner(source, fileName)
    tokens = scanner.scanTokens()

    # Stop if there was a syntax (scanning) error.
    if State.hadError:
        return

    parser = Parser(tokens)
    statements = parser.parse()

    # Stop if there was a syntax (parsing) error.
    if State.hadError:
        return
    
    resolver = Resolver(interpreter)
    resolver.resolve(statements)

    # Stop if there was a resolution error.
    if State.hadError:
        return
    
    # Print out a warning for each unused variable after resolving is complete.
    # Must be done after resolving has fully concluded so that warnings 
    # can be done only once and in order.
    # Warnings only issued if no resolve errors (or errors before that) occured; 
    # personal design choice to limit warn/error messages.
    resolver.varWarnings(resolver.localVars)

    interpreter.interpret(statements)

    if State.switchCLI: # User chose to switch to CLI while debugging (final: cannot switch back).
        State.inAFile = False
        # Clearing input buffer.
        # import os
        # if os.name == "nt": # Using Windows.
        #     import msvcrt
        #     while msvcrt.kbhit():
        #         msvcrt.getch()
        # else: # POSIX.
        #     # Cannot import termios at the beginning since 
        #     # it doesn't work on Windows.
        #     import termios
        #     termios.tcflush(sys.stdin, termios.TCIFLUSH)
        runPrompt()

def piping(path: str, baseName: str):
    if "Error" in path:
        # To re-direct errors to the given file as well.
        fd = None # For scope purposes.
        try:
            fd = open(f"Testing/Output/{baseName}Error.txt", "r+")
        except FileNotFoundError:
            fd = open(f"Testing/Output/{baseName}Error.txt", "w+")
        sys.stderr = fd
    else:
        fd = None
        try:
            fd = open(f"Testing/Output/{baseName}Output.txt", "r+")
        except FileNotFoundError:
            fd = open(f"Testing/Output/{baseName}Output.txt", "w+")
        sys.stdout = fd

def runFile(path, baseName = None):
    import State
    State.inAFile = True

    try:
        with open(path, "r") as file:
            lineList = file.readlines()
            lineList = [line.rstrip() for line in lineList]
            State.fileLines[path] = lineList
        with open(path, "r") as file:
            content = file.read()
        if testMode:
            piping(path, baseName)
        if testMode and ("Error" in path):
            for line in State.fileLines[path]:
                # We run each line separately so errors for each line
                # do not affect the next line running.
                # We reset the errors each time so they still execute separately.
                run(line, path)
                State.hadError = False
                State.hadRuntimeError = False
        else:
            run(content, path)
    except FileNotFoundError as error:
        sys.stderr.write(f"Could not run. File not found: {error.filename}.\n")
        sys.exit(66)

    if not testMode:
        if State.hadError:
            sys.exit(65)
        
        if State.hadRuntimeError:
            sys.exit(70)

    # Must reset error flags here so that each test file
    # can run with freshly reset flags, allowing it to execute successfully.
    else:
        State.hadError = False
        State.hadRuntimeError = False

def runPrompt():
    while True:
        lines = []
        print(">>>", end = " ")
        line = input("")
        if line == "":
            break
        if line[-1] == "\\":
            lines.append(line[:-1])
        else:
            lines.append(line)
        while line[-1] == "\\":
            # Replace the \ with a newline.
            # Not only removing the \ since that will combine separate lines.
            # This would cause problems if we don't indent (add a \t separator)
            # between consequent lines.
            line = line[:-1] + "\n"
            originalLen = len(line)
            line += input("... ")
            if line[-1] == "\\":
                newLine = line[originalLen:-1]
            else:
                newLine = line[originalLen]
            if (newLine != "") and (newLine != "\n"):
                lines.append(newLine)
        import State
        State.fileLines["_REPL_"] = lines
        run(line)
        if not State.debugMode:
            State.hadError = False

def error(error: BaseError):
    if type(error) == ScanError:
        report(error, "")
    elif error.token.type == TokenType.EOF:
        report(error, " at end")
    else:
        report(error, " at '" + error.token.lexeme + "'")

# Scan errors are treated differently since they are issued before 
# the formation of any tokens in the first place.
# Length = 0 -> token = EOF (no significant column value).
def report(error: BaseError, where: str):
    # Scan errors are different since there are no tokens whose fields we can use.
    line = error.line if (type(error) == ScanError) else error.token.line
    column = error.column if (type(error) == ScanError) else error.token.column
    message = error.message
    lexerFile = error.file if (type(error) == ScanError) else None

    sys.stderr.write(error.__class__.__name__[:-5] + " ")
    
    import State
    # In debug mode, we treat commands as REPL prompts (and accordingly for error reporting).
    if (State.debugMode or not linePos):
        sys.stderr.write(f'error: {message}\n')
        return

    lexemeLen = 1
    if lexerFile == None:
        lexemeLen = len(error.token.lexeme)

    file = lexerFile or error.token.fileName or "_REPL_"
    fileText = "" if (file == "_REPL_") else f"\"{file}\", "
    if lexemeLen == 0:
        sys.stderr.write(f'error{where} [{fileText}line {line}]: {message}\n')
        if linePrint:
            printErrorLine(line, file)
    elif lexemeLen == 1:
        sys.stderr.write(f'error{where} [{fileText}line {line}, {column}]: {message}\n')
        if linePrint:
            printErrorLine(line, file, column, column)
    else:
        sys.stderr.write(f'error{where} [{fileText}line {line}, {column}-{column + lexemeLen - 1}]: {message}\n')
        if linePrint:
            printErrorLine(line, file, column, column + lexemeLen - 1)

    if type(error) == RuntimeError:
        State.hadRuntimeError = True
    else:
        State.hadError = True

def warn(warning):
    import State
    # All warnings that we have (thus far) are given based on
    # static analysis of the code, while debug mode is only
    # on at runtime.
    # Thus, there would be no point altering the warnings to
    # fit the debugger.
    if State.debugMode:
        return

    line = warning.token.line
    column = warning.token.column
    lexemeLen = len(warning.token.lexeme)
    file = warning.token.fileName

    if not linePos:
        sys.stderr.write(f'Warning: {warning.message}')
        return

    fileText = "" if (file == "_REPL_") else f"\"{file}\", "
    if lexemeLen == 1: 
        sys.stderr.write(f'Warning [{fileText}line {line}, {column}]: ' + warning.message)
    else:
        sys.stderr.write(f'Warning [{fileText}line {line}, {column}-{column + lexemeLen - 1}]: ' + warning.message)

# Not available for REPL (why add it?).
# Start and end set to None initially in case of error being at end of line.
def printErrorLine(line: int, file: str, start = None, end = None):
    import State
    # rstrip used so a potential newline at the end of a line does not impact our error message.
    printLine = State.fileLines[file][line - 1].rstrip('\n') # -1 since line is minimum 1.
    # Strip all the whitespace on the left-side of the line, and record 
    # how much it is shifted to the left (to move the arrows 
    # to the left by the same amount).
    prevLineLen = len(printLine)
    printLine = printLine.lstrip()
    newLineLen = len(printLine)
    if start != None:
        start -= (prevLineLen - newLineLen)
        end -= (prevLineLen - newLineLen)
        sys.stderr.write(f"{line} |\t{printLine}\n")
        # Fill space before second vertical bar to align with above line.
        sys.stderr.write(" ".ljust(len(str(line)) + 1, " "))
        sys.stderr.write("|\t" + (" " * (start - 1)))
        sys.stderr.write("^" * (end - start + 1) + '\n')
    else:
        sys.stderr.write(f"{line} |\t{printLine}\n")
        sys.stderr.write(" ".ljust(len(str(line)) + 1, " "))
        sys.stderr.write("|\t" + (" " * newLineLen) + "^\n")
    sys.stderr.flush()

def fileNameCheck(path):
    if (len(path) < 4) or (path[-4:] != ".lox"):
        sys.stderr.write("Invalid lox file.\n")
        sys.exit(64) # Same issue (bad usage), so same exit code.

def test():
    from importlib import import_module
    import os
    import sys
    sys.path.append(os.getcwd() +  "\\Testing\\Python Files")
    module = import_module("generateTests")
    generateFunc = getattr(module, "generateTestFiles")
    generateFunc("tests")
    with open("Testing/testList.txt") as f:
        lines = f.readlines()
        if len(lines) == 0:
            print("No test files available.")
            exit(0)
        for line in lines:
            if line[-1] == '\n':
                line = line[:-1]
            path = "Testing/Tests/" + line
            fileNameCheck(path)
            runFile(path, line[:-4])
            path = "Testing/Tests/" + line[:-4] + "Error.lox"
            fileNameCheck(path)
            runFile(path, line[:-4])

def clean():
    import os
    lines = list()
    with open("Testing/testList.txt") as f:
        lines = f.readlines()
        for line in lines:
            if line[-1] == '\n':
                line = line[:-1]
    if len(lines) == 0:
        print("No test files to clean.")
        exit(0)
    for line in lines:
        paths = []
        paths.append(f"Testing/Python Files/test_{line[:-4]}.py")
        paths.append(f"Testing/Output/{line[:-4]}Output.txt")
        paths.append(f"Testing/Output/{line[:-4]}Error.txt")
        for path in paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError as error:
                        sys.stderr.write(f"Error cleaning test file {path}:\n{str(error)}")

def main():
    if len(sys.argv) == 1:
        runPrompt()
    elif len(sys.argv) == 2:
        if testMode:
            test()
        elif cleanMode:
            clean()
        elif Error:
            runPrompt()
        else:
            fileNameCheck(fileName)
            runFile(fileName)
    else:
        sys.stderr.write("Usage: plox [option or script]\n")
        sys.exit(64)

if __name__ == "__main__":
    main()