#### The debugger itself is quite straightforward, though it has a number of features. It is made to be similar to (though of course much simpler than) the GDB and PDB (Python) command-line debuggers. It therefore simply uses a number of instructions and commands (the former take no arguments while the latter do). Below are its features and instructions/commands with instruction on how to use them.

## Basic Usage

### Running the Debugger
To get the debugger to run on a piece of code, simply use the ```breakpoint()``` function where you would like a breakpoint to be inserted.\
Writing note: the naming similarity to Python's built-in ```breakpoint()``` function was entirely coincidental.\
The breakpoint function will automatically launch the debugger prompt.\
**Note:** instructions and commands are not followed by semi-colons.

### Debugger Errors
While executing particular instructions or commands, you might make a mistake, leading an error message to be presented. As with running the REPL, these errors will be non-fatal (i.e., the file execution and/or the debugger prompt will continue to run).\
The errors that appear in the debugger have also been simplified beyond what might appear in the regular REPL or during file-execution.\
Errors that appear in the debugger may be specific to it (e.g., ill-formed commands) or from the interpreter itself (e.g., displaying the value of an uninitialized variable).

### Entering Instructions
As stated prior, instructions are prompt inputs which take no arguments. For any instruction, you can enter its full name, e.g., ```continue```, or an abbreviated form of it which is usually the first letter (```c``` in this example). The exact abbreviation is stated below for each instruction. Trying to add any arguments after an instruction will lead to a debugger error.

### Entering Commands
Commands, as was mentioned, are like instructions, except that they require arguments.\
Some commands (e.g., v/value) may also require specific modifiers to properly execute. These modifiers will always be after the command and before its arguments. If you make a mistake in excluding these modifiers, a debugger error will be presented.\
Commands can accept any context-appropriate arguments, though the arguments cannot contain spaces (e.g., ```a + 1``` is not allowed, and may be interpreted by some commands to be multiple arguments).

## Debugger Instructions
#### Parts between parentheses (if any) in instruction names may be ommitted when using the instruction.

### ```c(ontinue)```
* This works identically to the ```continue``` command in other debuggers.
* It will exit the debugger and continue file-execution, only returning to the debugger if another breakpoint is reached.
* **Note**: an empty prompt input in the debugger will default to the ```continue``` instruction, exiting the debugger and resuming file-execution.

### ```s(tep)```
* Work in progress.

### ```n(ext)```
* Work in progress.

### ```q(uit)```
* Ends all code execution, both in the debugger and from the file.

### ```r(epl)```
* Ends file-execution and exits the debugger, opening a REPL Lox shell.
* The shell effectively follows on from the execution of the file, so any variables/objects in scope up until the breakpoint was hit remains defined within this shell.

### ```l(ist)```
* Presents the context of the breakpoint, printing it with the two lines above it and the two lines below it.
* If there are less than two lines above it or below it (independently), it prints however many there are for each, respectively.
* Current work on varying the number of lines to match a user-inputted value, making this a command instead.

### ```st(ack)```
* Displays the current call-stack (all the function calls currently 'active' or being executed).

### ```log```
* Displays the trace-log for the program (all the function calls, including nested calls, run since execution of the file commenced).

## Debugger Commands
#### Parts between parentheses (if any) in command names may be ommitted when using the command.

### ```v(alue)```
* Argument #: 2
* Argument Form:
    * A scope modifier (```l```/```local``` for variables defined in the current scope; ```g```/```global``` for variables defined in the global scope). Variable scope is determined by lexical scope relative to where the breakpoint is. As an example:
        ```
        fun makebreak()
        {
            breakpoint();
        }

        var x = 1;
        makebreak();
        ```
        No variables are in scope where the actual ```breakpoint()``` call is, and thus no objects will show with either option.
    * Any expression (can involve variables). Cannot contain any spaces.
* Prints out the value of the given expression.
* Examples:
    * ```v l a```
    * ```value global x```

### ```vars```
* Argument #: 1
* Argument Form:
    * A scope modifier (```local``` or ```global``` strictly).
* Prints out all the variables defined within the specified scope.
* **Note:** the ```local``` option will only show variables *declared* within the local scope, not those that are in scope but declared outside it.
* Example:
    * ```vars global```

### ```b(reak)```
* Argument #: any number
* Argument(s) Form:
    * A regular integer.
* Will make a breakpoint at the lines with the same numbers as the passed arguments if those lines have not already been passed by the breakpoint function call.
* Work in progress.
* Example:
    * ```break 4 10```