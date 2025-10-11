class Stmt:
	class Break:
		def __init__(self, breakCMD, loopType):
			self.breakCMD = breakCMD
			self.loopType = loopType

		def accept(self, visitor):
			visitor.visitBreakStmt(self)

	class Block:
		def __init__(self, statements):
			self.statements = statements

		def accept(self, visitor):
			visitor.visitBlockStmt(self)

	class Class:
		def __init__(self, name, superclass, private, public, classMethods):
			self.name = name
			self.superclass = superclass
			self.private = private
			self.public = public
			self.classMethods = classMethods

		def accept(self, visitor):
			visitor.visitClassStmt(self)

	class Continue:
		def __init__(self, continueCMD, loopType):
			self.continueCMD = continueCMD
			self.loopType = loopType

		def accept(self, visitor):
			visitor.visitContinueStmt(self)

	class Error:
		def __init__(self, body, errors, handler):
			self.body = body
			self.errors = errors
			self.handler = handler

		def accept(self, visitor):
			visitor.visitErrorStmt(self)

	class Expression:
		def __init__(self, expression):
			self.expression = expression

		def accept(self, visitor):
			visitor.visitExpressionStmt(self)

	class Fetch:
		def __init__(self, mode, name):
			self.mode = mode
			self.name = name

		def accept(self, visitor):
			visitor.visitFetchStmt(self)

	class Function:
		def __init__(self, name, params, body, defaults):
			self.name = name
			self.params = params
			self.body = body
			self.defaults = defaults

		def accept(self, visitor):
			visitor.visitFunctionStmt(self)

	class Group:
		def __init__(self, name, vars, functions, classes):
			self.name = name
			self.vars = vars
			self.functions = functions
			self.classes = classes

		def accept(self, visitor):
			visitor.visitGroupStmt(self)

	class If:
		def __init__(self, condition, thenBranch, elseBranch):
			self.condition = condition
			self.thenBranch = thenBranch
			self.elseBranch = elseBranch

		def accept(self, visitor):
			visitor.visitIfStmt(self)

	class List:
		def __init__(self, name, initializer):
			self.name = name
			self.initializer = initializer

		def accept(self, visitor):
			visitor.visitListStmt(self)

	class Match:
		def __init__(self, value, cases, default):
			self.value = value
			self.cases = cases
			self.default = default

		def accept(self, visitor):
			visitor.visitMatchStmt(self)

	class Print:
		def __init__(self, expression):
			self.expression = expression

		def accept(self, visitor):
			visitor.visitPrintStmt(self)

	class Report:
		def __init__(self, keyword, exception):
			self.keyword = keyword
			self.exception = exception

		def accept(self, visitor):
			visitor.visitReportStmt(self)

	class Return:
		def __init__(self, keyword, value):
			self.keyword = keyword
			self.value = value

		def accept(self, visitor):
			visitor.visitReturnStmt(self)

	class Var:
		def __init__(self, name, equals, initializer, access, static):
			self.name = name
			self.equals = equals
			self.initializer = initializer
			self.access = access
			self.static = static

		def accept(self, visitor):
			visitor.visitVarStmt(self)

	class While:
		def __init__(self, condition, body):
			self.condition = condition
			self.body = body

		def accept(self, visitor):
			visitor.visitWhileStmt(self)