from io import TextIOWrapper
import os

def defineAST(directory: str, classes: list[str], file: TextIOWrapper) -> None:
    file.write(f"class {directory}:\n")

    for entry in classes:
        parts = entry.split(":")
        className = parts[0].strip()
        fields = parts[1].split(",")

        file.write(f"\tclass {className}:\n")
        file.write(f"\t\tdef __init__(self")
        for field in fields:
            field = field.strip()
            file.write(f", {field}")
        file.write("):\n")

        for field in fields:
            field = field.strip()
            file.write(f"\t\t\tself.{field} = {field}\n")

        file.write("\n")
        file.write("\t\tdef accept(self, visitor):\n")
        if directory == "Stmt":
            file.write(f"\t\t\tvisitor.visit{className}{directory}(self)\n\n")
        else:
            file.write(f"\t\t\treturn visitor.visit{className}{directory}(self)\n\n")

ExprClasses = [ "Access     : object, operator, start, end",
                "Assign     : name, equals, value",
                "Binary     : left, operator, right",
                "Call       : callee, leftParen, rightParen, arguments",
                "Comma      : expressions",
                "Get        : object, name",
                "Grouping   : expression",
                "Lambda     : params, body, defaults",
                "List       : elements, operator",
                "Literal    : value",
                "Logical    : left, operator, right",
                "Modify     : part, operator, value",
                "Set        : object, name, value, visibility",
                "Super      : keyword, method",
                "Ternary    : condition,  trueBranch,  falseBranch",
                "This       : keyword",
                "Unary      : operator, right",
                "Variable   : name"]

StmtClasses = [ "Break      : breakCMD, loopType",
                "Block      : statements",
                "Class      : name, superclass, private, public, classMethods",
                "Continue   : continueCMD, loopType",
                "Error      : body, errors, handler",
                "Expression : expression",
                "Fetch      : mode, name",
                "Function   : name, params, body, defaults",
                "Group      : name, vars, functions, classes",
                "If         : condition, thenBranch, elseBranch",
                "List       : name, initializer",
                "Match      : value, cases, default",
                "Print      : expression",
                "Report     : keyword, exception",
                "Return     : keyword, value",
                "Var        : name, equals, initializer, access, static",
                "While      : condition, body"]

scriptDir = os.path.dirname(__file__) # scriptDir = 'Lox/utils'

targetPath = os.path.join(scriptDir, "..", "Expr.py")
with open(os.path.abspath(targetPath), "w") as f:
    defineAST("Expr", ExprClasses, f)

targetPath = os.path.join(scriptDir, "..", "Stmt.py")
with open(os.path.abspath(targetPath), "w") as f:
    defineAST("Stmt", StmtClasses, f)