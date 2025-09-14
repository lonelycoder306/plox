class Stmt:
	class Break:
		def __init__(self, breakCMD, loopType):
			self.breakCMD = breakCMD
			self.loopType = loopType

		def accept(self, visitor):
			return visitor.visitBreakStmt(self)

	class Block:
		def __init__(self, statements):
			self.statements = statements

		def accept(self, visitor):
			return visitor.visitBlockStmt(self)

	class Class:
		def __init__(self, name, superclass, private, public, classMethods):
			self.name = name
			self.superclass = superclass
			self.private = private
			self.public = public
			self.classMethods = classMethods

		def accept(self, visitor):
			return visitor.visitClassStmt(self)

	class Continue:
		def __init__(self, continueCMD, loopType):
			self.continueCMD = continueCMD
			self.loopType = loopType

		def accept(self, visitor):
			return visitor.visitContinueStmt(self)

	class Error:
		def __init__(self, body, errors, handler):
			self.body = body
			self.errors = errors
			self.handler = handler

		def accept(self, visitor):
			return visitor.visitErrorStmt(self)

	class Expression:
		def __init__(self, expression):
			self.expression = expression

		def accept(self, visitor):
			return visitor.visitExpressionStmt(self)

	class Fetch:
		def __init__(self, mode, name):
			self.mode = mode
			self.name = name

		def accept(self, visitor):
			return visitor.visitFetchStmt(self)

	class Function:
		def __init__(self, name, params, body, defaults):
			self.name = name
			self.params = params
			self.body = body
			self.defaults = defaults

		def accept(self, visitor):
			return visitor.visitFunctionStmt(self)

	class If:
		def __init__(self, condition, thenBranch, elseBranch):
			self.condition = condition
			self.thenBranch = thenBranch
			self.elseBranch = elseBranch

		def accept(self, visitor):
			return visitor.visitIfStmt(self)

	class List:
		def __init__(self, name, initializer):
			self.name = name
			self.initializer = initializer

		def accept(self, visitor):
			return visitor.visitListStmt(self)

	class Print:
		def __init__(self, expression):
			self.expression = expression

		def accept(self, visitor):
			return visitor.visitPrintStmt(self)

	class Report:
		def __init__(self, keyword, exception):
			self.keyword = keyword
			self.exception = exception

		def accept(self, visitor):
			return visitor.visitReportStmt(self)

	class Return:
		def __init__(self, keyword, value):
			self.keyword = keyword
			self.value = value

		def accept(self, visitor):
			return visitor.visitReturnStmt(self)

	class Var:
		def __init__(self, name, equals, initializer, access):
			self.name = name
			self.equals = equals
			self.initializer = initializer
			self.access = access

		def accept(self, visitor):
			return visitor.visitVarStmt(self)

	class While:
		def __init__(self, condition, body):
			self.condition = condition
			self.body = body

		def accept(self, visitor):
			return visitor.visitWhileStmt(self)