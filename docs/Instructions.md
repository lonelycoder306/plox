#### Instructions are in alphabetical order by title.

### Debugger
* The debugger itself has a number of features, instructions, and parts, and thus deserves its own [Debugger](./Debugger.md) file.
### Lambdas
* You can simply create a lambda with the regular function definition syntax, but with the function name ommitted.
* The interpreter will automatically ignore any lambdas that are not assigned to a variable/stored somewhere, since they are effectively values.
* Lambdas can be called from whichever object/variable they are stored in, e.g., by the name of the variable they are assigned to or as an array element with the [] operator.
### Multi-line REPL prompt.
* Simply add a \ at the end of each line (except the very last).
* The \ can be put any number of spaces away (including zero) from the end of the line.
* It will be automatically deleted from the actual formatted string (so you don't need to worry about deleting it).
* Note: errors given on the prompt will treat it as a single long string, rather than a number of lines.