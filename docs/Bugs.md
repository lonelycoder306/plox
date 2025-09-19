#### This file will contain any documentation on yet-to-be-fixed bugs in the implementation.
#### Each bug will be given a descriptive, short title, a description (in words) with a reproducable example.
#### Bugs will be progressively removed from the document as they are fixed.
#### A bug description may be followed by an optional "Status" section which describes any partial progress (smaller impact, less affected cases, etc.) made on resolving the bug.

## Bug 1 - "Undefined Variable" Error for Range-For Loops in Functions
### Description
Any range-for loops within function bodies result in "undefined variable" errors, as the program is (for some reason) unable to find the iterable variable (following the colon in the loop header).\
This applies to both iterable variables passed as parameters, as well as iterables declared within the function itself.
### Example
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