'''
Features to implement:
1) Breakpoints (figure out a way to allow them to be added at function entry points as well).
2) Options:
- step (Execute current line and stop at next one; if current line contains a function call, enter the function.)
- next (Execute current line and stop at next one; if current line contains a function call, evaluate the call and go to the next line; do not step into the function.)
- continue (Continue executing until breakpoint, end, or error is reached.)
3) Inspect variables in scope (values and current local/global variables).
4) Show current line being executed and call stack.
5) Evaluating expressions (possibly involving variables) on the fly.
6) Safely stop execution and return to shell or prompt.
Possibly:
7) Show changes in values of expressions.
8) Allow user to specify number of surrounding lines printed with breakpoint.
9) Allow user to specify logging mode to print out all output and commands.
'''

# class breakpointStop(Exception):
#     def showOptions(self):
#         import State
#         if not State.inAFile: #Using REPL.
#             print("No debug breakpoint option for command-line interpreter.")
#             return

#         import sys
#         sys.stdout.write("- Press Enter to continue.\n") # Use sys.stdout.write() consistently to avoid mixing with print().
#         sys.stdout.write("- Press d/D for debug information.\n")
#         sys.stdout.write("- Press t/T to end execution and open the terminal.\n")
#         sys.stdout.write("- Press q/Q to quit.\n")

#         while True:
#             choice = input("")
#             match choice:
#                 case "":
#                     self.clearOptions()
#                     return
#                 case 'd':
#                     self.clearOptions()
#                     self.debugDump()
#                     return
#                 case 'D':
#                     self.clearOptions()
#                     self.debugDump()
#                     return
#                 case 't':
#                     State.switchCLI = True
#                     self.clearOptions()
#                     return
#                 case 'T':
#                     State.switchCLI = True
#                     self.clearOptions()
#                     return
#                 case 'q':
#                     self.clearOptions()
#                     exit(0)
#                 case 'Q':
#                     self.clearOptions()
#                     exit(0)
#                 case _:
#                     sys.stdout.write("Please enter a valid option (Enter, d/D, t/T, q/Q).\n")
    
#     def clearOptions(self):
#         import sys
#         for i in range(0,5):
#             # Using special ASCII characters.
#             # Move the cursor up one line.
#             sys.stdout.write('\x1b[1A')
#             # Clear the line.
#             sys.stdout.write('\x1b[2K')

#     def debugDump(self):
#         lineCount = 0 # How many lines to remove if clearDump() is run.
#         from State import debugTokens, debugStatements, debugEnv
#         import sys
#         sys.stdout.write("\nTokens constructed by scanner:\n")
#         lineCount += 1
#         for token in debugTokens:
#             sys.stdout.write(token.toString() + '\n')
#             lineCount +=1

#         lineCount += 1
#         # print("\nStatements constructed by parser:")
#         # for statement in debugStatements:
#         #     print(...) # Something here.
#         #     lineCount += 1
#         sys.stdout.write("\nVariables in scope:\n") # Scope display is work in progress.
#         lineCount += 1
#         # origEnv = debugEnv
#         while debugEnv != None: # Print out the variables in every environment (inner-most to outer-most, i.e., global).
#             for variable in debugEnv.values.keys():
#                 from Interpreter import Interpreter
#                 dummyInterpreter = Interpreter() # Just defined to use stringify().
#                 sys.stdout.write(f"{variable}: {dummyInterpreter.stringify(debugEnv.values[variable])}\n")
#                 lineCount += 1
#             debugEnv = debugEnv.enclosing
#         lineCount += 1
#         sys.stdout.write("\n- Press d/D to remove debug information and continue.\n")
#         sys.stdout.write("- Press Enter to keep debug information and continue.\n")
#         lineCount += 2
#         choice = input("")
#         while True:
#             match choice:
#                 case "":
#                     self.clearDump(2)
#                     return
#                 case 'd':
#                     self.clearDump(lineCount)
#                     return
#                 case 'D':
#                     self.clearDump(lineCount)
#                     return
#                 case _:
#                     "Please enter a valid option (Enter, d/D)."
        
#     def clearDump(self, lineCount):
#         import sys
#         for i in range(0, lineCount + 1):
#             # Move the cursor up one line.
#             sys.stdout.write('\x1b[1A')
#             # Clear the line.
#             sys.stdout.write('\x1b[2K')

class breakpointStop(Exception):
    def __init__(self, interpreter):
        self.breakpoints = []
        self.interpreter = interpreter
        # Implementing them as dictionaries allows us to make easier match-case structures later.
        # Instructions -> Do X.
        # Commands -> Do X with Y as argument(s).
        self.instructions = {"c": "continue", 
                             "s": "step", 
                             "n": "next", 
                             "q": "quit",
                             "t": "term",
                             "sh": "shell"}
        self.commands = {"v": "value",
                         "vars": "vars"}
        self.quit = False # Continue debug prompt so long as this is false.

    def debugStart(self):
        import State
        State.debugMode = True
        if not State.inAFile:
            print("No debug breakpoint option for command-line interpreter.")
            return

        while not self.quit:
            print("(debug)", end = " ")
            prompt = input("")
            if prompt == "":
                self.debugInstructions("continue")
            else:
                prompt = prompt.split()
                choice = prompt[0].strip()
                arguments = [x.strip() for x in prompt[1:]]
                if (choice in self.instructions.keys()) or (choice in self.instructions.values()):
                    choice = self.instructions.get(choice, choice) # If it is a key, return its value; if it is a value, return itself.
                    if len(arguments) == 0:
                        self.debugInstructions(choice)
                    else:
                        print("Instruction does not take arguments.")
                elif (choice in self.commands.keys()) or (choice in self.commands.values()):
                    choice = self.commands.get(choice, choice)
                    self.debugCommands(choice, arguments)
                else:
                    print("Not a valid command/instruction.")

    def debugInstructions(self, choice):
        match choice:
            case "continue":
                pass
                return
            case "step":
                pass
                return
            case "next":
                pass
                return
            case "term":
                import State
                State.switchCLI = True
                self.quit = True # It is never re-set to true during the session, so user cannot return to file execution or debugging.
                return
            case "shell":
                import State
                State.switchCLI = True
                self.quit = True
                return
            case "quit":
                self.quit = True
                return

    def debugCommands(self, command, arguments):
        match command:
            case "value": # Can evaluate expressions, but they must contain NO spaces.
                if len(arguments) == 0:
                    print("No argument provided.")
                    return
                from Lox import run
                run(f"print {arguments[0]};")
                return
            case "vars":
                if len(arguments) == 0:
                    print("No arguments provided.")
                    return
                elif len(arguments) > 1:
                    print("Too many arguments.")
                    return
                if arguments[0] == "local": # FIX.
                    import State
                    variables = State.debugEnv
                    # Must keep track of variables that have been printed.
                    # If a variable is declared in a deeper scope, we should not print it (or its value) if it was also declared in an outer scope.
                    printedVariables = []
                    print("Variables in local scope:")
                    while variables != None:
                        for var in variables.values:
                            value = self.interpreter.stringify(variables.values[var])
                            if var not in printedVariables:
                                print(f"{var}: {value}")
                            printedVariables.append(var)
                        variables = variables.enclosing
                elif arguments[0] == "global":
                    variables = self.interpreter.globals.values
                    print("Variables in global scope:")
                    for var in variables:
                        value = self.interpreter.stringify(variables[var])
                        print(f"{var}: {value}")