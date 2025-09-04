def defineAST(directory, classes, file):
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
                "Set        : object, name, value",
                "Super      : keyword, method",
                "Ternary    : condition,  trueBranch,  falseBranch",
                "This       : keyword",
                "Unary      : operator, right",
                "Variable   : name"]

StmtClasses = [ "Break      : breakCMD, loopType",
                "Block      : statements",
                "Class      : name, superclass, private, public, classMethods",
                "Continue   : continueCMD, loopType",
                "Error      : body, handler",
                "Expression : expression",
                "Fetch      : mode, name",
                "Function   : name, params, body, defaults",
                "If         : condition, thenBranch, elseBranch",
                "List       : name, initializer",
                "Print      : expression",
                "Report     : keyword, exception",
                "Return     : keyword, value",
                "Var        : name, equals, initializer",
                "While      : condition, body"]

import os

script_dir = os.path.dirname(__file__) # script_dir = 'Lox/utils'

target_path = os.path.join(script_dir, "..", "Expr.py")
with open(os.path.abspath(target_path), "w") as f:
    defineAST("Expr", ExprClasses, f)

target_path = os.path.join(script_dir, "..", "Stmt.py")
with open(os.path.abspath(target_path), "w") as f:
    defineAST("Stmt", StmtClasses, f)