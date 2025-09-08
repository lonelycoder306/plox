#### Instructions are in alphabetical order by title.

### Built-in Functions
* Those are too numerous to go over here in their entirety. However, the comments at the beginning of the [code file](../Lox/BuiltinFunction.py) should be sufficiently clear and detailed to explain what they all do, including the arguments they take.

### Debugger
* The debugger itself has a number of features, instructions, and parts, and thus deserves its own [Debugger](./Debugger.md) file.

### Default Parameters in Functions
* As is the case with most programming languages (e.g., Python), you can simply add a default value for any parameter in your function *declaration*.
* No default parameter can be followed by a regular (i.e., non-default) parameter. However, you can have multiple default parameters after each other. For example:
  ```
  fun nothing(a, b = 1, c = 2) {}

  fun problem(a = 1, b) {} // Error! Can't have a regular parameter after a default parameter.
  ```
* Any expression can be used as the default value for such a parameter, including lambdas (covered below).
* As is also the case with most programming languages, a default parameter's value will be bound to the parameter if no value is passed in its place as an argument when the function is called.

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
    * The path to the file must be passed.
    * Example: ```GetFile "FileDir/Example.lox";```.

### IO
* Input/output operations in this implementation can be split into user IO (covered in [this file](./userIO.md)) and file IO (covered in [this file](./fileIO.md)).

### Lambdas
* You can simply create a lambda with the regular function definition syntax, but with the function name ommitted.
* The interpreter will automatically ignore any lambdas that are not assigned to a variable/stored somewhere, since they are effectively values.
* Lambdas can be called from whichever object/variable they are stored in, e.g., by the name of the variable they are assigned to or as an array element with the [ ] operator.

### Lists
* Similar to the debugger, lists have a number of useful features and methods, so I've devoted a [List](./List.md) file to it on its own.

### Multi-line REPL Prompt
* Simply add a \ at the end of each line (except the very last).
* The \ can be put any number of spaces away (including zero) from the end of the line.
* It will be automatically deleted from the actual formatted string (so you don't need to worry about deleting it yourself).
* Note: errors given on the prompt will treat it as a single long string, rather than a number of lines.

### Testing and Clean-up
* The tests check expected output and error messages for a wide number of different test cases which check multiple features, including edge cases.
* The tests rely on pre-written test and expected output files, which can be found in the "Testing" directory (currently hidden). 
* The testing option can be used with the following command:\
  ```plox -test```
* This command generates all the necessary Python testing scripts, as well as executing the given Lox test files, organizing the output into a dedicated child directory in "Testing".
* After running the command, simply run: ```pytest```. This will use the Python testing scripts to give test results.
* To clean up the left-over Python testing files and output files, simply run:\
  ```plox -clean```
* **Note:** The file "testList.txt" and any files in the "Tests" child directory should ***not*** be deleted for the testing option to work.

### User-Defined Errors and Warnings
* As with other topics here, user-defined errors and warnings need a dedicated treatment, and are thus covered separately in [Exceptions](./Exceptions.md).

### Variadic Functions
* To declare a variadic function, simply put ```...``` where the variable list of arguments should start, like so:\
  ```fun nothing(...) {}```
* Variadic functions can also have regular (non-default) parameters *before* the ellipsis (...). For example:
  ```
  fun nothing(a, b, ...) {}
  fun problem(..., a) {} // Error! Can't have parameters after the ellipsis.
  fun anotherProblem(a = 1, ...) {} // Error! Can't have a default parameter before the ellipsis.
  ```
* Variadic functions can accept a total of 256 arguments (the maximum number a Lox function can accept).
* Variadic functions declared with only an ellipsis (...) can accept zero arguments (though ```vargs``` would be empty).
* ```vargs``` is not defined automatically for *non*-variadic functions (and thus there is no need to worry about name collisions).
* The variable list of arguments (following any regular arguments) will be saved in a list called ```vargs``` which can be accessed in the function body. For example:
  ```
  fun loop(...)
  {
    for (var i = 0; i < length(vargs); i++)
        print i;
  }

  fun mix(a, b, ...)
  {
    if (length(vargs) == 0)
        return a+b;
    else
    {
        var sum = a+b;
        for (var i = 0; i < length(vargs); i++)
            sum += vargs[i];
        return sum;
    }
  }
  ```