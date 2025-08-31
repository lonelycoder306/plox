'''
Features to implement:
1) Breakpoints (figure out a way to allow them to be added at function entry points as well). DONE.
2) Options:
- step (Execute current line and stop at next one; if current line contains a function call, enter the function.)
- next (Execute current line and stop at next one; if current line contains a function call, evaluate the call and go to the next line; do not step into the function.)
- continue (Continue executing until breakpoint, end, or error is reached.) DONE.
3) Inspect variables in scope (values and current local/global variables). DONE.
4) Show current line being executed and call stack.
5) Evaluating expressions (possibly involving variables) on the fly. DONE.
6) Safely stop execution and return to shell or prompt. DONE.
Possibly:
7) Show changes in values of expressions.
8) Allow user to specify number of surrounding lines printed with breakpoint.
9) Allow user to specify logging mode to print out all output and commands.
'''

from Error import RuntimeError, StopError
import State
class breakpointStop(Exception):
    def __init__(self, interpreter, environment, expr):
        self.breakpoints = []
        self.interpreter = interpreter
        self.environment = environment
        # Implementing them as dictionaries allows us to make easier match-case structures later.
        # Instructions -> Do X.
        # Commands -> Do X with Y as argument(s).
        self.instructions = {"c": "continue",
                             "s": "step",
                             "n": "next", 
                             "q": "quit",
                             "t": "term",
                             "sh": "shell",
                             "l": "list",
                             "st": "stack",
                             "log": "log"}
        # Replace 'term' and 'shell' with 'cli'?
        self.commands = {"v": "value",
                         "vars": "vars"}
        self.token = expr.callee.name
        self.quit = False # Continue debug prompt so long as this is false.

    def debugStart(self):
        State.debugMode = True # Will turn off some features or specifications in our interpreter.
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
            prompt = input("")
            if prompt == "":
                self.debugInstruction("continue")
            else:
                prompt = prompt.split()
                choice = prompt[0].strip()
                arguments = [x.strip() for x in prompt[1:]]
                if (choice in self.instructions.keys()) or (choice in self.instructions.values()):
                    choice = self.instructions.get(choice, choice) # If it is a key, return its value; if it is a value, return itself.
                    if len(arguments) == 0:
                        self.debugInstruction(choice)
                    else:
                        print("Instruction does not take arguments.")
                elif (choice in self.commands.keys()) or (choice in self.commands.values()):
                    choice = self.commands.get(choice, choice)
                    self.debugCommand(choice, arguments)
                else:
                    print("Not a valid command/instruction.")
        State.debugMode = False

    def debugInstruction(self, choice):
        match choice:
            case "continue":
                self.quit = True
                return
            case "step":
                pass
                return
            case "next":
                pass
                return
            case "term":
                State.switchCLI = True
                # It is never re-set to true during the session, 
                # so user cannot return to file execution or debugging.
                self.quit = True
                return
            case "shell":
                State.switchCLI = True
                self.quit = True
                return
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

    def debugCommand(self, command, arguments):
        match command:
            case "value": # Can evaluate expressions, but they must contain NO spaces.
                self.comm_value(arguments)
            case "vars":
                self.comm_vars(arguments)
    
    def comm_value(self, arguments):
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
                statements = Parser(tokens).parse()

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
                statements = Parser(tokens).parse()

                self.interpreter.environment = self.environment
                self.interpreter.interpret(statements)
            finally:
                self.interpreter.environment = prevEnv
    
    def comm_vars(self, arguments):
        if len(arguments) == 0:
            print("No arguments provided.")
            return
        elif len(arguments) > 1:
            print("Too many arguments.")
            return
        if arguments[0] == "local":
            variables = self.environment.values
            print("Objects in current scope:")
            for var in variables:
                value = self.interpreter.stringify(variables[var])
                print(f"{var}: {value}")
        elif arguments[0] == "global":
            variables = self.interpreter.globals.values
            print("Objects in global scope:")
            for var in variables:
                value = self.interpreter.stringify(variables[var])
                print(f"{var}: {value}")
        else:
            print("Invalid argument.")