# Introduction
This is my implementation of the AST interpreter from (the first half of) Robert Nystrom's book "Crafting Interpreters". While I've largely stuck to Nystrom's own implementation details and structure, I've altered some parts of the interpreter structure (including minor parts of the language specification) and added a number of useful (in my opinion, anyway) features.
I've include a brief list below of the implementation's basic features which can be found in Nystrom's original Java implementation, followed by a more detailed list of my own changes or additions to the interpreter.
### Note
Due to the constantly changing nature of this project, there may be some changes which I have (unfortunately) missed within this documentation. I will certainly try to make sure that doesn't happen, but my efforts in this regard will likely be imperfect. This document will be duly updated if any changes do come to mind which have been left out.

# Project Directory Structure
* Libraries - Pre-written .lox files you can use with the ```GetLib``` directive.
* Lox - All the main Python files for the interpreter.
    * LoxMain.py is the main file to run for the interpreter to work.
    * utils/ holds utility files that can be used for work with the interpreter, but are not used when it is running.
* Modules - Additional Python files that can be "hooked up" to the interpreter at runtime with the ```GetMod``` directive.
* docs - Project documentation.

# Requirements
To use the interpreter itself, all that is required is a Python version >= 3.10.\
However, some particular external features (like the testing option) may require other tools. To review those, please consult [brief requirements](./requirements.in) and [detailed requirements](./requirements.txt).

# Regular Features of plox
The main Lox language implementation supports:
* REPL prompt and file-execution options.
* Arithmetic expressions involving any of the four main arithmetic operators.
* Boolean expressions (including compound and nested expressions).
* Number (float), string, Boolean, function, class and class-instance objects.
  * All objects are first-class.
* User-defined functions.
* User-defined classes.
* Inheritance.
* Error messages for all interpreter stages (scanning, parsing, resolving, executing).

# Personal Modifications to plox
This is a brief list of the changes I've made to the language, including additions and modifications. They're not in any particular order.\
For a more detailed list with justification (brief or lengthy) for each change, please go to [Justification](./docs/Justification.md).\
For further instruction on how to make use of some of these features, please go to [Instructions](./docs/Instructions.md).
* Added a minimal command-line debugger.
* Added a testing and cleaning option.
    * Testing uses Pytest.
    * Cleaning removes unnecessary test files after testing is complete.
* Added a built-in list class.
    * List objects are heterogeneous, variable-length arrays.
    * Multiple methods are made available for List objects.
* Added multi-line support for REPL prompts.
* Added support for lambdas.
* Added modulus (%) and exponent (^) operators.
* Added support for the (C-syntax) ternary/conditional operator.
* Added multiple built-in functions (in a separate environment).
* Added support for the (C-syntax) comma operator.
* Added default parameters for functions.
* Added importable userIO and fileIO modules.
* Added importable library files.
* Added scoped file imports.
* Improved error messages (with aesthetic display of error locations when running files).
    * Fun side-note: the file + line no. combination in the error/warning message can be used to immediately go to the problem location (at least if you're using the integrated terminal in VSCode).
    * Just hover over that part of the error/warning message until the "Open file in editor" option appears, or press Ctrl + click on that part of the message.
* Added user-defined exceptions (errors and warnings) and exception-handling.
* Added full encapsulation for classes.
    * Methods (non-static) can be made private with the 'safe' modifier before the function name.
    * Fields declared in the constructor can also be made private with the 'safe' modifier at the beginning.
* Added support for nested multi-line comments (/**/ syntax).
* Added (C-syntax) 'break' and 'continue' commands.
* Modified string literal form to distinguish between single-line and multi-line strings.
    * "" for single-line, `` for multi-line (similar to JS).
* Made strings mutable.
* Added declarations for variadic functions.
* Added support for range-for loops.
* Added namepaces (called "groups").
* Added fixed-value variables.
* Added support for user-defined printing functions on user-defined classes.
* Added support for user-defined comparison operators on user-defined classes.
* Added unique switch-/match-case ("match-is") structure with modifiable fallthrough behavior.
* Added command-line argument access (which can be nicely combined with file IO).

# Brief Q&A
This section will hopefully address some shorter questions regarding more significant design choices or simple inquiries concerning the interpreter and project as a whole.

### Are there any bugs in this implementation?
Possibly a few. I've tried my best to weed them all out with (hopefully) good solutions. If you do find any issues that I've missed, feel free to make an issue or pull request and I'll be happy to look at it. Feel free to also make non-bug-related suggestions on the implementation, which I might consider merging.\
Any bugs that have been found by myself or others and have yet to be fully resolved will be found (with sufficient information on the bug) in [Bugs](./docs/Bugs.md).

# Further Information
...
