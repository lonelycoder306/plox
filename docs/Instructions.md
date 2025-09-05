#### Instructions are in alphabetical order by title.

### Built-in Functions
* Those are two numerous to go over here in their entirety, and thus I've relegated comments on them to their own [Built-ins](./Built-ins.md) file.

### Debugger
* The debugger itself has a number of features, instructions, and parts, and thus deserves its own [Debugger](./Debugger.md) file.

### IO
* Input/output operations in this implementation can be split into user IO (covered in [this file](./userIO.md)) and file IO (covered in [this file](./fileIO.md)).

### Lambdas
* You can simply create a lambda with the regular function definition syntax, but with the function name ommitted.
* The interpreter will automatically ignore any lambdas that are not assigned to a variable/stored somewhere, since they are effectively values.
* Lambdas can be called from whichever object/variable they are stored in, e.g., by the name of the variable they are assigned to or as an array element with the [] operator.

### Lists
* Similar to the debugger, lists have a number of useful features and methods, so I've devoted a [List](./List.md) file to it on its own.

### Multi-line REPL prompt.
* Simply add a \ at the end of each line (except the very last).
* The \ can be put any number of spaces away (including zero) from the end of the line.
* It will be automatically deleted from the actual formatted string (so you don't need to worry about deleting it).
* Note: errors given on the prompt will treat it as a single long string, rather than a number of lines.