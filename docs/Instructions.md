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
* All imports are scope, i.e., they follow the same variable binding and shadowing rules as regular objects in the language, and do not apply outside the scope in which the import is made.\
**Note:** Imports are done by accessing files through particular paths. For them to work, the interpreter ***must*** be run from within the project's root directory.

* There are three main import directives supported:
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

### Fixed-Value Variables
* To declare a fixed value variable, simply use the ```fix``` modifier in place of ```var```, as below:
  ```
  fix x = 1;
  ```
* As is the case in other languages with this feature, you can access this variable freely. However, attempting to assign to it after it has been declared will result in an error:
  ```
  fix x = 1;
  x = 2; // Error! Fixed variable 'x' cannot be re-assigned.
  ```
* A fixed variable must be provided with an initializer. Not providing one will result in an error.
* Currently, only regular variables can be made fixed, leaving behind lists and fields. This may be extended in the future.

### Groups/Namespaces
* A group/namespace in this context is simply a scope for certain variables. Since Lox has first-class functions and classes, a variable here can be any declared object, such as a regular variable, a list object, a function, or a class.
* To declare a group, use the below syntax:
  ```
  group GroupName
  {
    [declaration 1...];
    [declaration 2...];
    [declaration 3...];
    [...]
  }
  ```
* To access a particular group member, simply use the same syntax for accessing a field off a class instance:
  ```
  print GroupName.Variable;
  GroupName.Function();
  var x = GroupName.Class();
  ```
* A group may only contain declarations. No other statements may be placed within a group (though they can off course be present in the bodies of function or class group members).
* Once a group is defined, its class members (even if uninitialized) cannot be reassigned. However, if they are modifiable (e.g., lists), they can still be modified after the group is defined.
* Group members can be used inside other group members. For example, the following works as expected:
  ```
  group A
  {
    var x = 1;
    fun show() {print x;}
  }

  A.show(); // Prints 1.
  ```
* Declarations and statements inside groups still follow lexical scoping. Thus, in the previous example, the ```x``` in ```show()``` always resolves to the variable ```x``` declared just above it.
* Though perhaps not recommended for good, readable code, it is allowed to nest groups. Access to group members works the same way. As an example:
  ```
  group A
  {
    group B
    {
        var x = 1;
    }
  }

  print A.B.x; // Prints 1.
  print B.x; // Error! "B" is undefined.
  ```

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

### Range-For Loops
* To construct a range-for loop, use either of the following syntaxes:
  1. ```
     for (var [iterator variable]: [iterable object]) {...}
     // Example:
     for (var i: [1,2,3]) {...}
     ```
  2. ```
     var [iterator variable] = [insert value];
     for ([iterator variable]: [iterable object]) {...}
     // Example:
     var i;
     list a = [1,2,3];
     for (i: a) {...}
     ```
* The iterable object can be a list, a string, or anything that evaluates to either of those.

### Match-Is Structure
* To write a match-is structure, use the following syntax:
  ```
  match ([expr])
    is [value 1]:
        [statement]
    is [value 2]:
        [statement]
  ```
* If the expr between () matches any of the listed values, the statement below the is-statement will be executed.
* If (for some reason) a value is repeated in another is-statement, only the first will be run. In other words, once the structure finds a match, it will terminate (by default).
  ```
  match (1)
    is 1:
        print 1; // Only this one will run.
    is 1:
        print 2;
  ```
* The match-is structure does not have fallthrough behaviour enabled by default. To enable fallthrough behavior, simply add the keyword ```fallthrough``` at the end of the case that you wish fallthrough to occur after (assuming the case hits a match):
  ```
  match (1)
    is 1:
        print 1; // This will run.
        fallthrough
    is 2:
        print 2; // This will also run.
  ```
* To add a default case (which will unconditionally run *if no prior case matches*), simply put an _ in place of the case value:
  ```
  match (1)
    is 2:
        print 2;
    is _:
        // This will run if no prior case matches.
        print "No match.";
* Some notes:
  * It is necessary to place whatever the match expression is between parentheses.\
    Parentheses are entirely optional for any of the cases below it.
  * The ```fallthrough``` keyword is ***not*** followed by a semicolon. 
  * The ```fallthrough``` keyword should always be at the *end* of the case. If the statement following the check (```is [expr]:```) is a block, keep the keyword *outside* the block.
  * The default case (if any) will also run if fallthrough behavior is enabled.
  * There is no issue in excluding the default case altogether. This will not result in any warnings or errors.
* Since the structure internally uses comparison to verify a case-hit, the usability of the structure for complex, custom-type objects remains a work in progress.

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

### User-Defined Comparison Operators
* Users can overload the main comparison operators (==, !=, >, >=, <, <=) for their own custom classes by adding the following methods to their classes with the class-specific definition for these operators:

  |   Operator   |     Method     |
  |:------------:|:--------------:|
  |   ```==```   |    ```_eq```   |
  |   ```!=```   |    ```_ne```   |
  |   ```>```    |    ```_gt```   |
  |   ```>=```   |    ```_ge```   |
  |   ```<```    |    ```_lt```   |
  |   ```<=```   |    ```_le```   |
* These methods *must* return a Boolean value, or an error will result.\
  They must also each take a single argument, which will be the RHS of the comparison expression.
* The appropriate method will only run if two instances of the same class are being compared; otherwise, they will not be used, and an error will result if the operator is an inequality operator (since the instances cannot be compared with such an operator).
* If a particular method is not defined, the interpreter will default to the built-in comparison operators.

### User-Defined Errors and Warnings
* As with other topics here, user-defined errors and warnings need a dedicated treatment, and are thus covered separately in [Exceptions](./Exceptions.md).

### User-Defined Print Output for Classes
* If users wish to have custom output be printed if a person attempts to print an instance of their custom class, they can define the ```_str``` method in their class.
* The method must take *no* parameters and must return a string, or an error will result.

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