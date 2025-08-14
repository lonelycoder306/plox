from Environment import Environment
from LoxCallable import LoxCallable
from LoxClass import LoxClass
from LoxInstance import LoxInstance
from Error import RuntimeError
import io

'''
Needed operations:
- File handling.
1) Creating a file (cannot already exist) - path/name.
2) Opening a file (must already exist) - path/name.
3) Checking if a file exists - path/name.
4) Closing a file - fd.
Additional: handle multiple input/output streams.

- File input.
1) Reading X characters from a file - fd.
2) Reading X bytes from a file (as bytes) - fd.
3) Reading a word from a file - fd.
4) Reading a line from a file - fd.
5) Reading entire file into a single string - fd.
6) Reading entire file (or certain number of lines) into list of lines - fd.
Additional: add option in each one to shift or not shift file pointer.

- File output.
1) Write string to a file (default is to overwrite, option exists to append) - fd.
2) Write to a particular position in the file - fd.

- General operations.
1) Move cursor in a file to position X - fd.
2) Move cursor in a file back or forward by Y steps - fd.
3) Move cursor to very beginning or very end - fd.
4) Check if cursor is at the end of the file - fd.

'''

fileIO = Environment()
functions = ["filemake", "fileopen", "filehas", "filedrop",
             "filechars", "filebytes", "fileword", "fileline", "filelines", "fileall",
             "filewrite", "fileput",
             "filejump", "fileskip", "filelimits", "feof"]

class fileFunction(LoxCallable):
    def __init__(self, mode: str):
        self.mode = mode
        self.fd = io.StringIO()
        self.position = 0

    def bind(self, fileObj):
        self.fd = fileObj.fields.get("fd", None)
    
    def call(self, interpreter, expr, arguments):
        try:
            self.check(expr, arguments)
        except RuntimeError as error:
            raise error
        
        match self.mode:
            case "filemake":
                try:
                    return self.f_filemake(arguments[0], expr)
                except RuntimeError as error:
                    raise error
            case "fileopen":
                try:
                    return self.f_fileopen(arguments[0], expr)
                except RuntimeError as error:
                    raise error
            case "filehas":
                return self.f_filehas(arguments[0], expr)
            case "filedrop":
                self.f_filedrop()

            case "filechars":
                return self.f_filechars(int(arguments[0]), expr)
            case "filebytes":
                return self.f_filebytes(int(arguments[0]), expr)
            case "fileword":
                return self.f_fileword(expr)
            case "fileline":
                return self.f_fileline(expr)
            case "filelines":
                return self.f_filelines(int(arguments[0]), expr)
            case "fileall":
                return self.f_fileall(expr)
            
            case "filewrite":
                self.f_filewrite(arguments[0], arguments[1], expr)
            case "fileput":
                self.f_fileput(arguments[0], arguments[1], expr)
            
            case "filejump":
                self.f_filejump(arguments[0], expr)
            case "fileskip":
                self.f_fileskip(arguments[0], expr)
            case "filelimits":
                self.f_filelimits(arguments[0], expr)
            case "feof":
                return self.f_feof(expr)
    
    # ------------------------------------------------------------

    # File handling.

    def f_filemake(self, path, expr):
        try:
            instance = LoxInstance(fileRef)
            open(path, "x").close() # Just create the file.
            instance.fields["fd"] = open(path, "r+")
            return instance
        except FileExistsError:
            raise RuntimeError(expr.callee.name, "File already exists.")

    def f_fileopen(self, path, expr):
        try:
            instance = LoxInstance(fileRef)
            instance.fields["fd"] = open(path, "r+")
            return instance
        except FileNotFoundError:
            raise RuntimeError(expr.callee.name, "File does not exist.")
    
    def f_filehas(self, path, expr):
        from pathlib import Path
        return Path(path).is_file()
    
    def f_filedrop(self):
        self.fd.close()
    
    # File input.

    def f_filechars(self, n: int, expr):
        try:
            previous = self.fd.tell()
            chars = self.fd.read(n)
            self.fd.seek(previous)
            return chars
        except ValueError: # File is closed.
            raise RuntimeError(expr.callee.name, "File is closed.")
    
    def f_filebytes(self, n: int, expr):
        try:
            file = open(self.fd, "rb") # Opening here again to read as bytes instead.
            previous = self.fd.tell()
            nbytes = file.read(n)
            self.fd.seek(previous)
            return nbytes
        except ValueError:
            raise RuntimeError(expr.callee.name, "File is closed.")
    
    def f_fileword(self, expr):
        try:
            previous = self.fd.tell()
            c = ""
            word = ""
            fd = self.fd
            while True:
                if c.isspace():
                    c = fd.read(1)
                else:
                    break
            while True:
                c = fd.read(1)
                if c.isspace() or (c == ""): # Check for EOF.
                    break
                word += c
            self.fd.seek(previous)
            return word
        except ValueError:
            raise RuntimeError(expr.callee.name, "File is closed.")
    
    def f_fileline(self, expr):
        try:
            previous = self.fd.tell()
            line = self.fd.readline()
            self.fd.seek(previous)
            return line
        except ValueError:
            raise RuntimeError(expr.callee.name, "File is closed.")
    
    def f_filelines(self, n, expr):
        try:
            previous = self.fd.tell()
            filelines = self.fd.readlines()
            self.fd.seek(previous)
            return filelines
        except ValueError:
            raise RuntimeError(expr.callee.name, "File is closed.")
    
    def f_fileall(self, expr):
        try:
            previous = self.fd.tell()
            file = self.fd.read()
            self.fd.seek(previous)
            return file
        except ValueError:
            raise RuntimeError(expr.callee.name, "File is closed.")
    
    # File output.
    
    def f_filewrite(self, string: str, format: bool, expr):
        try:
            self.fd.write(string)
        except ValueError:
            raise RuntimeError(expr.callee.name, "File is closed.")
    
    # Will not change cursor position (use jump then write instead for that).
    def f_fileput(self, string: str, pos: int, expr):
        try:
            previous = self.fd.tell()
            self.fd.seek(pos)
            self.fd.write(string)
            self.fd.seek(previous)
        except ValueError:
            raise RuntimeError(expr.callee.name, "File is closed.")

    # General operations.

    def f_filejump(self, pos: int, expr):
        try:
            self.fd.seek(pos)
        except ValueError:
            raise RuntimeError(expr.callee.name, "File is closed.")

    def f_fileskip(self, skip: int, expr):
        try:
            position = self.fd.tell()
            self.fd.seek(position + skip)
        except ValueError:
            raise RuntimeError(expr.callee.name, "File is closed.")

    def f_filelimits(self, option: str, expr):
        try:
            match option:
                case "b":
                    self.fd.seek(0,0)
                case "e":
                    self.fd.seek(0,2)
        except ValueError:
            raise RuntimeError(expr.callee.name, "File is closed.")

    def f_feof(self, expr) -> bool:
        try:
            previous = self.fd.tell()
            if self.fd.read(1) == "":
                return True
            self.fd.seek(previous) # Only return to original position if not at end.
            return False
        except ValueError:
            raise RuntimeError(expr.callee.name, "File is closed.")

    # ------------------------------------------------------------

    # Error checking.

    def check(self, expr, arguments):
        match self.mode:
            case "filemake":
                return self.check_filemake(expr, arguments)
            case "fileopen":
                return self.check_fileopen(expr, arguments)
            case "filehas":
                return self.check_filehas(expr, arguments)
            case "filedrop":
                return self.check_filedrop(expr, arguments)

            case "filechars":
                return self.check_filechars(expr, arguments)
            case "filebytes":
                return self.check_filebytes(expr, arguments)
            case "fileword":
                return self.check_fileword(expr, arguments)
            case "fileline":
                return self.check_fileline(expr, arguments)
            case "filelines":
                return self.check_filelines(expr, arguments)
            case "fileall":
                return self.check_fileall(expr, arguments)
            
            case "filewrite":
                return self.check_filewrite(expr, arguments)
            case "fileput":
                return self.check_fileput(expr, arguments)
            
            case "filejump":
                return self.check_filejump(expr, arguments)
            case "fileskip":
                return self.check_fileskip(expr, arguments)
            case "filelimits":
                return self.check_filelimits(expr, arguments)
            case "feof":
                return self.check_feof(expr, arguments)

    # ------------------------------------------------------------

    def check_filemake(self, expr, arguments):
        if type(arguments[0]) == str:
            return True
        raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                       "Types are: string.")

    def check_fileopen(self, expr, arguments):
        if type(arguments[0]) == str:
            return True
        raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                       "Types are: string.")

    def check_filehas(self, expr, arguments):
        if type(arguments[0]) == str:
            return True
        raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                       "Types are: string.")

    def check_filedrop(self, expr, arguments):
        return True

    def check_filechars(self, expr, arguments):
        if type(arguments[0]) == float:
            return True
        raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number.")

    def check_filebytes(self, expr, arguments):
        if type(arguments[0]) == float:
            return True
        raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number.")

    def check_fileword(self, expr, arguments):
        return True

    def check_fileline(self, expr, arguments):
        return True

    def check_filelines(self, expr, arguments):
        if type(arguments[0]) == float:
            return True
        raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number.")

    def check_fileall(self, expr, arguments):
        return True

    def check_filewrite(self, expr, arguments):
        if (type(arguments[0]) == str)  and (type(arguments[1]) == bool):
            return True
        raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                       "Types are: string, boolean.")

    def check_fileput(self, expr, arguments):
        if (type(arguments[0]) == str)  and (type(arguments[1]) == float):
            return True
        raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                       "Types are: string, number.")

    def check_filejump(self, expr, arguments):
        if type(arguments[0]) == float:
            return True
        raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number.")

    def check_fileskip(self, expr, arguments):
        if type(arguments[0]) == float:
            return True
        raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                       "Types are: number.")

    def check_filelimits(self, expr, arguments):
        if type(arguments[0]) == str:
            return True
        raise RuntimeError(expr.callee.name, "Arguments do not match accepted parameter types.\n" \
                                       "Types are: string.")

    def check_feof(self, expr, arguments):
        return True

    # ------------------------------------------------------------

    def arity(self):
        match self.mode:
            case "filemake":
                return 1
            case "fileopen":
                return 1
            case "filehas":
                return 1
            case "filedrop":
                return 0
            case "filechars":
                return 1
            case "filebytes":
                return 1
            case "fileword":
                return 0
            case "fileline":
                return 0
            case "filelines":
                return 1
            case "fileall":
                return 0
            case "filewrite":
                return 2
            case "fileput":
                return 2
            case "filejump":
                return 1
            case "fileskip":
                return 1
            case "filelimits":
                return 1
            case "feof":
                return 0

fileRef = LoxClass("file", {})
def fileIOSetUp():
    for function in functions[:3]:
        fileIO.define(function, fileFunction(function))
    for function in functions[3:]:
        fileRef.methods[function] = fileFunction(function)