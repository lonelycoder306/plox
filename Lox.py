import sys
from Token import TokenType
from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from Resolver import Resolver
from Error import LexError, ParseError, ResolveError, RuntimeError

fileName = None
if len(sys.argv) == 2:
    fileName = sys.argv[1]

interpreter = Interpreter()

def run(source):
    import State

    scanner = Scanner(source)
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
    # Must be done after resolving has fully concluded so that warnings can be done only once and in order.
    # Warnings only issued if no resolve errors (or errors before that) occured; personal design choice to limit warn/error messages.
    resolver.varWarnings(resolver.localVars)

    interpreter.interpret(statements)

    if State.switchCLI: # User chose to switch to CLI while debugging (final: cannot switch back).
        State.inAFile = False
        runPrompt()

def runFile(path):
    import State

    try:
        with open(path, "r") as file:
            State.fileLines = file.readlines()
        with open(path, "r") as file:
            content = file.read()
        State.inAFile = True
        run(content)
    except FileNotFoundError:
        sys.stderr.write("Could not run. File not found.\n")
        sys.exit(66)

    if State.hadError:
        sys.exit(65)
    
    if State.hadRuntimeError:
        sys.exit(70)

def runPrompt():
    while True:
        print(">>>", end = " ")
        line = input("")
        if line == "":
            break
        run(line)
        import State
        if State.debugMode: # Do not issue proper errors while in debug mode.
            State.debugError = True
        else:
            State.hadError = False

def lError(error: LexError): #lError: line-error
    report(error, error.line, error.column, "", error.message)

def tError(error: ParseError | ResolveError): #tError: token-error
    if error.token.type == TokenType.EOF:
        report(error, error.token.line, error.token.column, " at end", error.message)
    else:
        report(error, error.token.line, error.token.column, " at '" + error.token.lexeme + "'", error.message)

# Nested if blocks are mainly checking two things:
# 1) If there is a file name (no file name = REPL being used).
# 2) If the token the error was found at contains multiple characters or not.
# If it does, the error message will contain the exact area (beginning and ending) containing the token.
# If it doesn't, the error message will contain only the column containing the (single-character) token.
# Lex errors are treated differently since they are issued before the formation of any tokens in the first place.
# Length = 0 -> token = EOF (no significant column value).
def report(error, line, column, where, message):
    if type(error) == LexError:
        sys.stderr.write("Scan ")
    elif type(error) == ParseError:
        sys.stderr.write("Parse ")
    elif type(error) == ResolveError:
        sys.stderr.write("Resolve ")
    import State
    if type(error) != LexError: # Lex errors are different since there are no tokens whose fields we can use.
        if (fileName != None) and (not State.debugMode): # In debug mode, we treat commands as REPL prompts (and accordingly for error reporting).
            if len(error.token.lexeme) == 0:
                sys.stderr.write(f'error{where} ["{fileName}", line {line}]: {message}\n')
                printErrorLine(line)
            elif len(error.token.lexeme) == 1:
                sys.stderr.write(f'error{where} ["{fileName}", line {line}, {column}]: {message}\n')
                printErrorLine(line, column, column)
            else:
                lexemeLen = len(error.token.lexeme)
                sys.stderr.write(f'error{where} ["{fileName}", line {line}, {column}-{column + lexemeLen - 1}]: {message}\n')
                printErrorLine(line, column, column + lexemeLen - 1)
        else: # Using REPL.
            offset = State.debugOffset
            if len(error.token.lexeme) == 0:
                sys.stderr.write(f'error{where}: {message}\n')
            elif len(error.token.lexeme) == 1:
                sys.stderr.write(f'error{where} [{column - offset}]: {message}\n')
            else:
                lexemeLen = len(error.token.lexeme)
                sys.stderr.write(f'error{where} [{column - offset}-{column + lexemeLen - 1 - offset}]: {message}\n')
    else: # Lex Error.
        if (fileName != None) and (not State.debugMode):
            sys.stderr.write(f'error{where} ["{fileName}", line {line}, {column}]: {message}\n')
            printErrorLine(line, column, column)
        else:
            offset = State.debugOffset
            sys.stderr.write(f'error{where} [{column - offset}]: {message}\n')
    State.hadError = True

def runtimeError(error: RuntimeError):
    line = error.token.line
    column = error.token.column
    lexemeLen = len(error.token.lexeme)
    import State
    if (fileName != None) and (not State.debugMode):
        if lexemeLen == 0:
            sys.stderr.write(f'Runtime error ["{fileName}", line {line}]: {error.message}\n')
            printErrorLine(line)
        elif lexemeLen == 1:
            sys.stderr.write(f'Runtime error ["{fileName}", line {line}, {column}]: {error.message}\n')
            printErrorLine(line, column, column)
        else:
            sys.stderr.write(f'Runtime error ["{fileName}", line {line}, {column}-{column + lexemeLen - 1}]: {error.message}\n')
            printErrorLine(line, column, column + lexemeLen - 1)
    else: # No point in printing the line since the REPL interpreter will always consider the prompt to be line 1.
        offset = State.debugOffset
        if lexemeLen == 0:
            sys.stderr.write(f'Runtime error: {error.message}\n')
        elif lexemeLen == 1:
            sys.stderr.write(f'Runtime error [{column - offset}]: {error.message}\n')
        else:
            sys.stderr.write(f'Runtime error [{column - offset}-{column + lexemeLen - 1 - offset}]: {error.message}\n')
    if State.debugMode:
        State.debugError = True
    else:
        State.hadRuntimeError = True

def warn(warning):
    line = warning.token.line
    column = warning.token.column
    lexemeLen = len(warning.token.lexeme)
    import State
    if (fileName != None) and (not State.debugMode):
        if lexemeLen == 1: 
            sys.stderr.write(f'Warning ["{fileName}", line {line}, {column}]: ' + warning.message)
        else:
            sys.stderr.write(f'Warning ["{fileName}", line {line}, {column}-{column + lexemeLen - 1}]: ' + warning.message)
    else:
        if lexemeLen == 1: 
            sys.stderr.write(f'Warning [line {line}, {column}]: ' + warning.message)
        else:
            sys.stderr.write(f'Warning [line {line}, {column}-{column + lexemeLen - 1}]: ' + warning.message)


# Not available for REPL (why add it?).
# Start and end set to None initially in case of error being at end of line.
def printErrorLine(line: int, start = None, end = None):
    import State
    # rstrip used so a potential newline at the end of a line does not impact our error message.
    printLine = State.fileLines[line - 1].rstrip('\n') # -1 since line is minimum 1.
    # Strip all the whitespace on the left-side of the line, and record how much it is shifted to the left (to move the arrows to the left by the same amount).
    prevLineLen = len(printLine)
    printLine = printLine.lstrip()
    newLineLen = len(printLine)
    if start != None:
        start -= (prevLineLen - newLineLen)
        end -= (prevLineLen - newLineLen)
        sys.stderr.write(f"{line} |\t{printLine}\n")
        space = " "
        sys.stderr.write(space.ljust(len(str(line)) + 1, " ")) # Fill space before second vertical bar to align with above line.
        sys.stderr.write("|\t")
        sys.stderr.write(" " * (start - 1))
        sys.stderr.write("^" * (end - start + 1) + '\n')
    else:
        sys.stderr.write(f"|\t{printLine}\n")
        space = " "
        sys.stderr.write(space.ljust(len(str(line)) + 1, " "))
        sys.stderr.write("|\t")
        sys.stderr.write(" " * newLineLen)
        sys.stderr.write("^\n")
    sys.stderr.flush()

def main():
    if len(sys.argv) > 2:
        sys.stderr.write("Usage: plox [script]\n")
        sys.exit(64)
    elif len(sys.argv) == 2:
        if (len(fileName) < 4) or (fileName[-4:] != ".lox"):
            sys.stderr.write("Invalid lox file.\n")
            sys.exit(64) # Same issue (bad usage), so same exit code.
        runFile(sys.argv[1])
    else:
        runPrompt()

if __name__ == "__main__":
    main()