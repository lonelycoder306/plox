#### Below are instructions on how to import the userIO module and the various functions it provides.

## Importing userIO
Importing the module itself is quite trivial. All you need to do is write:\
```GetMod "userIO";```\
The command must be written exactly like that, or the module will not be recognized (or some other error may result).\
The module import is scoped, meaning that if the module is imported in a particular scope, its variable-binding pairs (name-value) will not persist outside of that scope (avoiding name collisions).

## Available Functions
### inchars(n, delim = false)
* The function reads at most n characters from stdin and returns a string containing the characters it read.
* delim being true will end character-reading if the function hits a new-line (the new-line character will be discarded), even if it has not yet read n characters.
* If delim is false, the function will accept new-line characters and continue reading.

### inbytes(n, delim = false)
* This function works identically to inchars, except for two differences:
  1. It reads the input as a series of bytes, returning it as such.
  2. If delim is set to true, it breaks at \n and \r characters.

### inline()
* The function reads a line from stdin, and returns a string containing the line.
* The new-line character marking the end of the line is discarded.
  
### inlines(n = -1)
* If n is specified by the user, the function reads n lines from stdin and returns a list containing each line read as a string.
* If n is not specified, the function reads all the lines available and returns a list containing each line read as a string.

### inpeek()
* A quick function to read a character from stdin and return it.

### echo()
* Our ```print``` command does not format string arguments when printing them, so "Hello\n" would be printed exactly as it is.
* This function formats its string argument, accounting for escape characters.
* The function strictly only accepts string arguments.

### inflush()
* Flushes the buffer for stdin.

### outflush()
* Flushes the buffer for stdout.