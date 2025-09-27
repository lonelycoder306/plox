#### This file will contain any documentation on yet-to-be-fixed bugs in the implementation.
#### Each bug will be given a descriptive, short title, a description (in words) and some reproducable example(s). The descriptions will also include any ascertained information on which files containing the bug-causing code.
#### Bugs will be progressively removed from the document as they are fixed.
#### A bug description may be followed by an optional "Status" section which describes any partial progress (smaller impact, less affected cases, etc.) made on resolving the bug.

## Bug 1 - "Undefined Variable" Error for Range-For Loops in Functions
### Description
Any range-for loops within function bodies result in "undefined variable" errors, as the program is (for some reason) unable to find the iterable variable (following the colon in the loop header).\
This applies to both iterable variables passed as parameters, as well as iterables declared within the function itself.
#### Location: Unknown
### Example(s)
Example 1:
```
fun show(array)
{
    for (var i : array) print i;
}

show([1,2,3]); // Runtime error: Undefined variable or function 'array'.
```

Example 2:
```
fun show()
{
    list array = [1,2,3];
    for (var i : array) print i;
}

show(); // Runtime error: Undefined variable or function 'array'.
```
### Status
No official progress on diagnosing or fixing this bug, though with some debugging work, it seems like this might be an issue with our environment-hopping, since the interpreter is always trying to fetch the iterable variable from the global scope (unsurprisingly hitting an error when it doesn't find it there). This is clearer still given that the following code runs without issue:
```
list array = [1,2,3];
fun show()
{
    for (var i : array) print i;
}

show();
// Prints:
// 1
// 2
// 3
```

## Bug 2 - Incorrect Resolving for Function-Object Parameters in Lists
### Description
If a function object (whether declared as a regular function or a lambda) is stored in a list, and happens to have parameters with the same name as the list it is stored in, any calls to that function from within the list will make resolve the parameter to the list, ignoring any arguments/input.
#### Location: Unknown
### Example(s)
Example 1:
```
list a = [fun(a) { print a; }];
a[0](1);
// Should print: 1
// Actually prints: [<lambda>] (i.e., the list a)
```

Example 2:
```
fun show(a)
{
    print a;
}
list a = [show];
a[0](1);
// Should print: 1
// Actually prints: [<fn show>]
```
### Status
The main bug here has been resolved. The fix consisted of switching the variable resolving so that we fetch values from the current environment before searching the global scope. Doing the opposite (which is what originally occurred) would lead to the problem above, since we resolve to the global list ```a``` (in the above example) rather than the local parameter variable. The look-up code snippet (as of writing this):
``` python
if distance != None:
    value = self.environment.getAt(distance, name)
    return value
else:
    if name.lexeme in self.environment.values.keys():
        return self.environment.get(name)
    elif name.lexeme in self.globals.values.keys():
        return self.globals.get(name)
    return self.builtins.get(name)
```
However, there are still issues with this solution, since any local variable (even in the current environment) should have a distance other than None associated with the variable expression containing it. Thus, if our static resolving code is working correctly, we should expect that the below if-clause be obsolete, since it searches the current environment directly (even though the check above it should already do this indirectly):
``` python
if name.lexeme in self.environment.values.keys():
    return self.environment.get(name)
```
The deeper issue here has yet to be located/diagnosed.