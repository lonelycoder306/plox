# File to handle multiple shared ("global") variables across interpreter files.

# For handling command-line arguments to the interpreter (used in LoxMain).
fileName: str
testMode = False
cleanMode = False
Error = False # True if "-error" or "-linepos" options have been used.
linePos = False # True if line-position info should be printed.
linePrint = False # True if error lines should be printed.

# For error-handling.
hadError = False # If a lex error, parse error, or resolve error occurred during their respective stages.
hadRuntimeError = False # If a runtime error occurred during the interpreter stage.
# Dictionary containing all the lines in the file being executed (to print out lines containing errors) 
# with their associated file name.
fileLines = dict()

# For debug option (files only).
inAFile = False # Whether or not we are running a file or command-line prompts.
switchCLI = False # Whether or not to end file execution and switch to terminal CLI.
debugMode = False # Whether or not we are in a debug session (will alter format of error-reporting).
debugError = False
callStack = list()
traceLog = list()
breakpoints = []

replDebug = False

# For access to private fields within methods.
inMethod = False
currentClass = None