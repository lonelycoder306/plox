# File only exists to avoid making any global error variables in Lox.py
# Global variables led to severe bugs and wrong hadError or hadRuntimeError variables being modified.
# Fixed with the use of this file.

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
debugError = False # Different error variable for any errors that occur during a debug prompt session (to not impact system exits or exit codes).

# For access to private fields within methods.
inMethod = False