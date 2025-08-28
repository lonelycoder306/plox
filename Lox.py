import sys
from Token import TokenType
from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from Resolver import Resolver
from Error import LexError, ParseError, ResolveError, RuntimeError

fileName = None
testMode = False
cleanMode = False
linePrint = True
if len(sys.argv) == 2:
    if sys.argv[1] == "-test":
        testMode = True
        linePrint = False
    if sys.argv[1] == "-clean":
        cleanMode = True
        linePrint = False
    else:
        fileName = sys.argv[1]

interpreter = Interpreter()

def run(source, fileName = None):
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
        runPrompt()

def runFile(path, baseName = None):
    import State
    State.inAFile = True

    try:
        with open(path, "r") as file:
            State.fileLines[path] = file.readlines()
        with open(path, "r") as file:
            content = file.read()
        if testMode:
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
        print(">>>", end = " ")
        line = input("")
        if line == "":
            break
        while line[-1] == "\\":
            line = line[:-1]
            line += input("... ")
        run(line)
        import State
        if State.debugMode: # Do not issue proper errors while in debug mode.
            State.debugError = True
        else:
            State.hadError = False

def lError(error: LexError): #lError: line-error
    report(error, error.line, error.column, "", error.message, error.file)

def tError(error: ParseError | ResolveError): #tError: token-error
    if error.token.type == TokenType.EOF:
        report(error, error.token.line, error.token.column, " at end", error.message)
    else:
        report(error, error.token.line, error.token.column, " at '" + error.token.lexeme + "'", error.message)

# Nested if blocks are mainly checking two things:
# 1) If there is a file name (no file name = REPL being used).
# 2) If the token the error was found at contains multiple 
# characters or not.
# If it does, the error message will contain the exact area 
# (beginning and ending) containing the token.
# If it doesn't, the error message will contain only the column 
# containing the (single-character) token.
# Lex errors are treated differently since they are issued before 
# the formation of any tokens in the first place.
# Length = 0 -> token = EOF (no significant column value).
def report(error, line, column, where, message, lexerFile = None):
    if type(error) == LexError:
        sys.stderr.write("Scan ")
    elif type(error) == ParseError:
        sys.stderr.write("Parse ")
    elif type(error) == ResolveError:
        sys.stderr.write("Resolve ")
    import State

    if State.debugMode:
        sys.stderr.write(f'error{where}: {message}\n')
        return

    # Lex errors are different since there are no tokens whose fields we can use.
    if type(error) != LexError:
        file = error.token.fileName
        # In debug mode, we treat commands as REPL prompts (and accordingly for error reporting).
        if (file != None) and (not State.debugMode):
            if len(error.token.lexeme) == 0:
                sys.stderr.write(f'error{where} ["{file}", line {line}]: {message}\n')
                if linePrint:
                    printErrorLine(line, file)
            elif len(error.token.lexeme) == 1:
                sys.stderr.write(f'error{where} ["{file}", line {line}, {column}]: {message}\n')
                if linePrint:
                    printErrorLine(line, file, column, column)
            else:
                lexemeLen = len(error.token.lexeme)
                sys.stderr.write(f'error{where} ["{file}", line {line}, {column}-{column + lexemeLen - 1}]: {message}\n')
                if linePrint:
                    printErrorLine(line, file, column, column + lexemeLen - 1)
        else: # Using REPL.
            if len(error.token.lexeme) == 0:
                sys.stderr.write(f'error{where}: {message}\n')
            elif len(error.token.lexeme) == 1:
                sys.stderr.write(f'error{where} [{column}]: {message}\n')
            else:
                lexemeLen = len(error.token.lexeme)
                sys.stderr.write(f'error{where} [{column}-{column + lexemeLen - 1}]: {message}\n')
    else: # Lex Error.
        if (lexerFile != None) and (not State.debugMode):
            sys.stderr.write(f'error{where} ["{lexerFile}", line {line}, {column}]: {message}\n')
            if linePrint:
                printErrorLine(line, lexerFile, column, column)
        else:
            sys.stderr.write(f'error{where} [{column}]: {message}\n')
    State.hadError = True

def runtimeError(error: RuntimeError):
    line = error.token.line
    column = error.token.column
    lexemeLen = len(error.token.lexeme)
    file = error.token.fileName
    import State

    if State.debugMode:
        sys.stderr.write(f'Runtime error: {error.message}\n')
        return

    # We only print a file name if there is one
    # and we aren't in the debugger.
    if (file != None) and (not State.debugMode):
        if lexemeLen == 0:
            sys.stderr.write(f'Runtime error ["{file}", line {line}]: {error.message}\n')
            if linePrint:
                printErrorLine(line, file)
        elif lexemeLen == 1:
            sys.stderr.write(f'Runtime error ["{file}", line {line}, {column}]: {error.message}\n')
            if linePrint:
                printErrorLine(line, file, column, column)
        else:
            sys.stderr.write(f'Runtime error ["{file}", line {line}, {column}-{column + lexemeLen - 1}]: {error.message}\n')
            if linePrint:
                printErrorLine(line, file, column, column + lexemeLen - 1)
    else: # No point in printing the line since the REPL interpreter will always consider the prompt to be line 1.
        if lexemeLen == 0:
            sys.stderr.write(f'Runtime error: {error.message}\n')
        elif lexemeLen == 1:
            sys.stderr.write(f'Runtime error [{column}]: {error.message}\n')
        else:
            sys.stderr.write(f'Runtime error [{column}-{column + lexemeLen - 1}]: {error.message}\n')
    # We don't want the debugger to quit if it hits an error,
    # like the REPL.
    if State.debugMode:
        State.debugError = True
    else:
        State.hadRuntimeError = True

def warn(warning):
    line = warning.token.line
    column = warning.token.column
    lexemeLen = len(warning.token.lexeme)
    file = warning.token.fileName
    import State
    if (file != None) and (not State.debugMode):
        if lexemeLen == 1: 
            sys.stderr.write(f'Warning ["{file}", line {line}, {column}]: ' + warning.message)
        else:
            sys.stderr.write(f'Warning ["{file}", line {line}, {column}-{column + lexemeLen - 1}]: ' + warning.message)
    else:
        if lexemeLen == 1: 
            sys.stderr.write(f'Warning [{column}]: ' + warning.message)
        else:
            sys.stderr.write(f'Warning [{column}-{column + lexemeLen - 1}]: ' + warning.message)

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
        space = " "
        # Fill space before second vertical bar to align with above line.
        sys.stderr.write(space.ljust(len(str(line)) + 1, " "))
        sys.stderr.write("|\t")
        sys.stderr.write(" " * (start - 1))
        sys.stderr.write("^" * (end - start + 1) + '\n')
    else:
        sys.stderr.write(f"{line} |\t{printLine}\n")
        space = " "
        sys.stderr.write(space.ljust(len(str(line)) + 1, " "))
        sys.stderr.write("|\t")
        sys.stderr.write(" " * newLineLen)
        sys.stderr.write("^\n")
    sys.stderr.flush()

def fileNameCheck(path):
    if (len(path) < 4) or (path[-4:] != ".lox"):
        sys.stderr.write("Invalid lox file.\n")
        sys.exit(64) # Same issue (bad usage), so same exit code.

def main():
    if len(sys.argv) > 2:
        sys.stderr.write("Usage: plox [script]\n")
        sys.exit(64)
    elif len(sys.argv) == 2:
        if testMode:
            import importlib
            module = importlib.import_module("Testing.Python Files.generateTests")
            generateFunc = getattr(module, "generateTestFiles")
            generateFunc()
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
        elif cleanMode:
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
                                sys.stderr.write(f"Error cleaning test files:\n{str(error)}")
        else:
            fileNameCheck(fileName)
            runFile(fileName)
    else:
        runPrompt()

if __name__ == "__main__":
    main()