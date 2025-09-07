#### Below are instructions on how to import the fileIO module and the various functions and methods it provides.

## Importing fileIO
Importing the module itself is quite trivial. All you need to do is write:\
```GetMod "fileIO";```\
The command must be written exactly like that, or the module will not be recognized (or some other error may result).\
The module import is scoped, meaning that if the module is imported in a particular scope, its variable-binding pairs (name-value) will not persist outside of that scope (avoiding name collisions).

## File Objects
Many of the functions defined in fileIO either return file objects, or are methods accessed through file objects.\
A file object is a runtime representations of what is internally a file descriptor that allows access to the actual file on disk.\
We shall first list functions that can be called directly, then list file object methods.

## Available Functions
#### These functions are for general handling of files. They do not carry out any input/output themselves.
#### Some methods (```filedrop``` and ```flush```) are also used for file-handling.

### filemake(path, makedirs = false, movepos = True)
* The function strictly creates a non-existent file with/at the given pathname (a regular name will create the file in the current directory).
* Thorough error-handling is implemented to catch possible errors with file-creation permissions, OS fails, improper path, etc.
* If the file already exists, an error will be raised.
* If ```makedirs``` is set to true, the function will try to create the given directory for the file if it does not already exist.
* If ```makedirs``` is set to/left as false, an error will be raised if a directory in the path given does not exist.
* If ```movepos``` is set to/left as true, any input/output operation on the file will freely move the cursor position as dictated by the operation.
* If ```movepos``` is set to false, the cursor position will remain unchanged by any input/output operation, and can only be changed by explicit position-changing functions (see below).
* The function returns a file object accessing the given file. The file will be open for reading/writing.

### fileopen(path, movepos = true)
* The function tries to open the file with the given pathname.
* If the file does not exist, an error is raised.
* If ```movepos``` is set to/left as true, any input/output operation on the file will freely move the cursor position as dictated by the operation.
* If ```movepos``` is set to false, the cursor position will remain unchanged by any input/output operation, and can only be changed by explicit position-changing functions (see below).
* The function returns a file object accessing the given file. The file will be open for reading/writing.

**Tip:**\
Use ```filehas()``` (see below) to check if a file exists first before trying to create or open it.\
If it doesn't exist, use ```filemake()```. If it does, use ```fileopen()```.

### filehas(path)
* Returns true if the file with the given pathname exists; returns false if it doesn't exist.

### fileremove(path)
* The function will attempt to remove the file with the given pathname (you **cannot** pass it a file object).
* If any errors are encountered with the OS will attempting to delete the file, the function will abort and show the OS' reported error.
* **Note:** Use ```filedrop()``` (see below) on an open file to close it before deleting it.\
  Attempting to remove a still open file (whether one opened by filemake or fileopen) will give an OS error (still the file is in use).

## Available Methods
#### These functions can only be called on a file object.
**Note:** The methods below will only work if the file is *open*.

### filedrop()
* Closes the file accessed through the file object it is called on.

### flush()
* Flushes the buffer for output to the file.

### Input Methods

### filechars(n, delim = false)
* Will read at most ```n``` characters from the file (starting from the cursor position).
* If ```delim``` is set to true, the character-reading will stop once a new-line character is reached (the new-line character itself is discarded).

### filebytes(n, delim = false)
* This function works identically to filechars, except for two differences:
  1. It reads the input as a series of bytes, returning it as such.
  2. If delim is set to true, it breaks at \n and \r characters.

### fileword()
* Reads a single word from the file (delimited by whitespace or the end of the file).
* Returns the word as a string.

### fileline()
* Reads a single line from the file (delimited by a new-line character or the end of the file).
* Returns the line as a string.

### filelines(n = -1)
* If ```n``` is not specified, it reads all the lines in the file.
* If ```n``` is specified, it reads at most ```n``` lines from the file (stopping early if EOF is reached).
* Returns the lines as a list, with each line being a string element in the list (in order).

### fileall()
* Reads the entire file into a single string, and returns the string.

### Output Methods

### filewrite(string, format = true)
* Will write the given string to the file.
* If ```format``` is set to/left as true, the string is first formatted to account for escape sequence characters.
* If ```format``` is set to false, the string is written to the file as-is.

### fileput(string, pos, format = true)
* Performs the same operation as ```filewrite```, but writes its string to the position in the file specified by ```pos```.
* Raises an error if the position given is beyond the end of the file.

### Cursor Position Methods
### filejump(pos)
* Moves the cursor to the specified position.
* Raises an error if the position is beyond the end of the file.

### fileskip(skip)
* Moves the cursor ```skip``` positions ahead of its current position.
* Raises an error if the position that should be reached is beyond the end of the file.

### filelimits(option)
* If ```option``` is "b", it moves the cursor to the beginning of the file.
* If ```option``` is "e", it moves the cursor to the end of the file.

### filepos()
* Returns the current position of the cursor in the file.

### feof()
* Returns true if the file end has been reached; returns false if it has not.