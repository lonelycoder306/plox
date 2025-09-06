#### Instructions are in alphabetical order by title.

### Built-in Functions
* Those are too numerous to go over here in their entirety. However, the comments at the beginning of the [code file](../Lox/BuiltinFunction.py) should be sufficiently clear and detailed to explain what they all do, including the arguments they take.

### Debugger
* The debugger itself has a number of features, instructions, and parts, and thus deserves its own [Debugger](./Debugger.md) file.

### File Imports
All imports are scope, i.e., they follow the same variable binding and shadowing rules as regular objects in the language, and do not apply outside the scope in which the import is made.\
**Note:** Imports are done by accessing files through particular paths. For them to work, the interpreter ***must*** be run from within the project's root directory.

There are three main import directives supported:
1. GetMod
    * This is used for modules (currently: userIO, fileIO).
    * This will make all functions and methods within these modules available for use.
    * Example: ```GetMod "userIO";```.
2. GetLib
    * This is used for library files (currently: Error, Map, Set, String, Warning).
    * As with modules, all functions, classes, and methods within these library files will be made available for use.
    * Only the file name is passed; no extension should be added.
    * Example: ```GetLib "Map";```.
3. GetFile
    * This is used with user-owned Lox files.
    * Passing non-Lox files will raise an error.
    * The relative path to the file must be passed.
    * Example: ```GetFile "FileDir/Example.lox";```.

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