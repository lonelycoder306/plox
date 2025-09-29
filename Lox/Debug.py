from __future__ import annotations
from typing import TYPE_CHECKING

from Environment import Environment
from Error import StopError
from Expr import Expr
import State

if TYPE_CHECKING:
    import Interpreter

'''
Features to implement:
1) Breakpoints (figure out a way to allow them to be added at function entry points as well). DONE.
2) Options:
- step (Execute current line and stop at next one; if current line contains a function call, enter the function.)
- next (Execute current line and stop at next one; if current line contains a function call, evaluate the call and go to the next line; do not step into the function.)
- continue (Continue executing until breakpoint, end, or error is reached.) DONE.
- out (Step out of the current executing function, if any, while executing the remainder of its body.)
3) Inspect variables in scope (values and current local/global variables). DONE.
4) Show current line being executed and call stack.
5) Evaluating expressions (possibly involving variables) on the fly. DONE.
6) Safely stop execution and return to shell or prompt. DONE.
Possibly:
7) Show changes in values of expressions.
8) Allow user to specify number of surrounding lines printed with breakpoint.
9) Allow user to specify logging mode to print out all output and commands.
'''

class CLISwitch(Exception):
    pass

class breakpointStop(Exception):
    def __init__(self, interpreter: Interpreter, environment: Environment, 
                 expr: Expr.Call) -> None:
        self.breakpoints = []
        self.interpreter = interpreter
        self.environment = environment
        # Implementing them as dictionaries allows us to make easier match-case structures later.
        # Instructions -> Do X.
        # Commands -> Do X with Y as argument(s).
        self.instructions = {"c":   "continue",
                             "s":   "step",
                             "n":   "next",
                             "o":   "out", 
                             "q":   "quit",
                             "r":   "repl",
                             "l":   "list",
                             "st":  "stack",
                             "log": "log",
                             "h":   "help",
                             "loc": "locals",
                             "gl":  "globals"}
        self.commands = {"v":       "value",
                         "b":       "break"}
        self.token = expr.callee.name
        self.quit = False # Continue debug prompt so long as this is false.

    def debugStart(self) -> None:
        # Will turn off some features or specifications in our interpreter.
        State.debugMode = True
        if not State.inAFile:
            print("No debug breakpoint option for command-line interpreter.")
            return

        fileName = self.token.fileName
        file = State.fileLines[fileName]
        line = self.token.line - 1
        # To avoid wrap-around and printing lines from the end
        # if a breakpoint is on the first line.
        if line > 0:
            print(f'("{fileName}", {line}) ->\t{file[line - 1].lstrip()}')
        else:
            print(f'("{fileName}", {line}) ->\t{file[line].lstrip()}')

        while not self.quit:
            print("(debug)", end = " ")
            # .strip() so the debugger doesn't choke on whitespace input.
            prompt = input("").strip()
            if prompt == "":
                break
            else:
                prompt = prompt.split()
                choice = prompt[0].strip()
                arguments = [x.strip() for x in prompt[1:]]
                if (choice in self.instructions.keys()) or (choice in self.instructions.values()):
                    # If it is a key, return its value; if it is a value, return itself.
                    choice = self.instructions.get(choice, choice)
                    if len(arguments) == 0:
                        self.debugInstruction(choice)
                    else:
                        print("Instruction does not take arguments.")
                elif (choice in self.commands.keys()) or (choice in self.commands.values()):
                    choice = self.commands.get(choice, choice)
                    self.debugCommand(choice, arguments)
                else:
                    print("Not a valid command/instruction. Type 'help' for a list of valid commands/instructions.")
        State.debugMode = False

    def debugInstruction(self, choice: str) -> None:
        match choice:
            case "continue":
                self.quit = True
                return
            case "step":
                return
            case "next":
                return
            case "out":
                return
            case "repl":
                # Cannot be reset.
                # Permanent switch to command-line.
                raise CLISwitch()
            case "quit":
                raise StopError()
            case "list":
                line = self.token.line - 1
                file = self.token.fileName
                lines = State.fileLines[file]
                line -= 2
                for i in range(0, 5):
                    if (line < 0) or (line >= len(lines)):
                        line += 1
                        continue
                    print(lines[line])
                    line += 1
            case "stack":
                for func in State.callStack:
                    print(f"(\"{func["file"]}\", {func["line"]}): {func["name"]}")
            case "log":
                for func in State.traceLog:
                    print(f"(\"{func["file"]}\", {func["line"]}): {func["name"]}")
            case "help":
                self.displayHelp()
            case "locals":
                variables = self.environment.values
                print("Objects in current scope:")
                for var in variables:
                    value = self.interpreter.stringify(variables[var])
                    print(f"{var}: {value}")
            case "globals":
                variables = self.interpreter.globals.values
                print("Objects in global scope:")
                for var in variables:
                    value = self.interpreter.stringify(variables[var])
                    print(f"{var}: {value}")
    
    def displayHelp(self) -> None:
        print(
'''Available commands:
        h(elp)      - Display this help screen.
        c(ontinue)  - Exit debugger and continue execution until breakpoint, error, or end is reached.
        s(tep)      - Go to the next line, and enter the function if it is a function call.
        n(ext)      - Go to the next line, and evaluate (but do not enter) the function if it is a function call.
        r(epl)      - End debug session and file execution and open a prompt shell.
        q(uit)      - Exit the debugger and conclude all code execution.
        l(ist)      - Display lines surrounding current breakpoint.
        st(ack)     - Display call-stack.
        log         - Display trace-log for the file up until the current breakpoint.
        loc(als)    - Display all the variables/objects declared in the current scope.
        gl(obals)   - Display all the variables/objects declared in the global scope.

Available instructions:
        v(alue) [l/local or g/global] (expr)    - Prints the value of the given expression within the given scope.
        break [line #]                          - Adds a breakpoint at the given line (if the line has yet to be passed).''')

    def debugCommand(self, command: str, arguments: list[str]) -> None:
        match command:
            case "value": # Can evaluate expressions, but they must contain NO spaces.
                self.comm_value(arguments)
            case "vars":
                self.comm_vars(arguments)
            case "break":
                self.comm_break(arguments)
    
    def comm_value(self, arguments: list[str]) -> None:
        options = ["l", "local", "g", "global"]
        if len(arguments) == 0:
            print("No arguments provided.")
            return
        
        elif len(arguments) == 1:
            if arguments[0] in options:
                print("No value argument.")
            else:
                print("No proper modifier (l/local, g/global).")
            return
        
        elif len(arguments) > 2:
            print("Too many arguments.")
            return

        if (arguments[0] == "g") or (arguments[0] == "global"):
            prevEnv = self.interpreter.environment
            try:
                from Scanner import Scanner
                from Parser import Parser
                tokens = Scanner(f"print {arguments[1]};", None).scanTokens()
                if State.debugError:
                    State.debugError = False # Reset.
                    return
                statements = Parser(tokens).parse()
                if State.debugError:
                    State.debugError = False
                    return

                self.interpreter.environment = self.interpreter.globals
                self.interpreter.interpret(statements)
            finally:
                self.interpreter.environment = prevEnv

        elif (arguments[0] == "l") or (arguments[0] == "local"):
            prevEnv = self.interpreter.environment
            try:
                from Scanner import Scanner
                from Parser import Parser
                tokens = Scanner(f"print {arguments[1]};", None).scanTokens()
                if State.debugError:
                    State.debugError = False
                    return
                statements = Parser(tokens).parse()
                if State.debugError:
                    State.debugError = False
                    return

                self.interpreter.environment = self.environment
                self.interpreter.interpret(statements)
            finally:
                self.interpreter.environment = prevEnv
    
    def comm_break(self, arguments: list[str]) -> None:
        if len(arguments) == 0:
            print("No line provided.")
            return
        for i, line in enumerate(arguments):
            if line.isdigit():
                line = int(line)
                if self.token.line <= line:
                    State.breakpoints.append(line)
                else:
                    if len(arguments) == 1:
                        print("Line has been passed.")
                    else:
                        print(f"Line no. {i+1} has been passed.")
                    return
            else:
                print("Invalid input type. Type is: positive integer.")
                return

class replDebugger():
    '''
    To add:
    - watch [...]
    - unwatch [...]
    - check [...]
    - uncheck [...]
    - exit
    '''

    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter = interpreter
        self.instructions = {}
        self.commands = {}
        self.watches: list[str] = []
        self.checks: list[str] = []
        self.exit = False

    def runDebugger(self) -> None:
        State.replDebug = True
        
        while not self.exit:
            print("(ldb)", end = " ")
            prompt = input("").strip()
            if prompt == "":
                continue
            else:
                prompt = prompt.split()
                choice = prompt[0].strip()
                arguments = [x.strip() for x in prompt[1:]]
            
        State.replDebug = False
    
    def addWatch(self, expr: Expr) -> None:
        self.watches.append(expr)

    def runWatches(self) -> None:
        from Scanner import Scanner
        from Parser import Parser
        statement = ""
        for watch in self.watches:
            statement += f"print \"{watch}: \" + ({watch});"
        tokens = Scanner(statement, None).scanTokens()
        statements = Parser(tokens).parse()

        self.interpreter.interpret(statements)
    
    def addCheck(self, expr: Expr) -> None:
        self.checks.append(expr)
    
    def runChecks(self) -> None:
        from Scanner import Scanner
        from Parser import Parser
        statement = ""
        for check in self.checks:
            statement += f"{check};"
        tokens = Scanner(statement, None).scanTokens()
        statements = Parser(tokens).parse()

        self.interpreter.interpret(statements)