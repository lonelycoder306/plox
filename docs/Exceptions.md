#### Below is relevant information on constructing user-defined exceptions (errors or warnings), reporting these exceptions, and exception-handling.

### Exception Objects
Exceptions in this implementation are class instances from either the ```Error``` class or the ```Warning``` class, or any subclass of either.\
Errors will, depending on how the user defines them, either cause all execution to be aborted, or only the current block.\
Warnings, on the other hand, will not prevent any code execution. They are simply presented to the user if they are not handled.
**Note:** Trying to report any other object (including instances from classes that do not fit this rule) will result in an error, since the object will not be recognized as a valid exception.

### Creating Exception Objects
#### This section will first explain how to create error objects, and thereafter any differences for warning objects will be mentioned.

To create an error object, you must first import the Error library file:\
```GetLib "Error";```
This will import the ```Error``` class which all error objects must be instances of (or instances of a subclass of ```Error```, as mentioned above).\
The ```Error``` class offers two important functions:
1. ```init(message, halt = true, code = nil)```
   * This is the constructor for the ```Error``` class.
   * ```message``` is the primary error message that you wish to be printed when that error is reported. Since it is specific to each error object, it can be made unique to that particular error.
   * ```halt``` is a parameter that instructs the interpreter to either abort all code execution (if ```halt``` is true) or only execution of the current block (if ```halt``` is false).
   * ```code``` is an introductory phrase that can be used to give a brief description of the error or its type (in reality it can be any string the user wishes to put there). If left as nil, no code is printed.
   * Example usage:
     ```
     var exception1 = Error("Wrong function usage.", false, "Function error");
     // Will be displayed as:
     // Function error: Wrong function usage.
     var exception2 = Error("Wrong input type.");
     // Will be displayed as:
     // Wrong input type.
     ```
2. ```show()```.
   * This method displays the complete error message for the error object it is called from.
   * This does not need to be called by the user for the error message to be printed. The message will automatically show if no handler exists.
   * The message is printed to **stderr**.

As for warning objects, the only differences are:
* You must import the Warning library file instead, and use the ```Warning``` class rather than the ```Error``` class:
  ```
  GetLib "Warning";
  var warning = Warning("Final warning.");
  ```
* Warning messages are printed to **stdout** rather than stderr.

### Reporting Errors or Warnings
For an error or warning object to actually be used in code, it must be placed within a *report* statement.\
The syntax for this statement is:\
```report [error/warning object];```\
In place of the square brackets, you can place anything that evaluates to an error or warning object, including variables or constructor calls for ```Error``` or ```Warning``` (or any child class of theirs).

### Exception-Handling
Of course, to properly implement exceptions, we want users to be able to catch both our runtime errors as well as their own user-defined errors.\
To do so, they should use an ```attempt-handle``` statement structure. The syntax of the structure is as below:\
```
attempt
    [Possibly problematic statement...]
handle
    [What to do if an error occurs above...]
```
* The new-lines after ```attempt``` and ```handle``` are (of course) not necessary.
* Any statement may be put after ```attempt``` or ```handle```, including an entire block.
* An ```attempt``` statement *must* be followed by a single ```handle``` statement.
* There is current work in progress for ```handle``` statements to specify particular types of errors to handle. For the moment, they will execute if *any* error (runtime errors or any user-defined errors) occur, and prevent the error from being presented to the user.
* Any errors that occur while executing ```handle``` statements will not themselves be handled.