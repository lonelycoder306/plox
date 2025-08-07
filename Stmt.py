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

	class Continue:
		def __init__(self, continueCMD, loopType):
			self.continueCMD = continueCMD
			self.loopType = loopType

		def accept(self, visitor):
			return visitor.visitContinueStmt(self)

	class Function:
		def __init__(self, name, params, body):
			self.name = name
			self.params = params
			self.body = body

		def accept(self, visitor):
			return visitor.visitFunctionStmt(self)

	class If:
		def __init__(self, condition, thenBranch, elseBranch):
			self.condition = condition
			self.thenBranch = thenBranch
			self.elseBranch = elseBranch

		def accept(self, visitor):
			return visitor.visitIfStmt(self)

	class Expression:
		def __init__(self, expression):
			self.expression = expression

		def accept(self, visitor):
			return visitor.visitExpressionStmt(self)

	class Print:
		def __init__(self, expression):
			self.expression = expression

		def accept(self, visitor):
			return visitor.visitPrintStmt(self)

	class Return:
		def __init__(self, keyword, value):
			self.keyword = keyword
			self.value = value

		def accept(self, visitor):
			return visitor.visitReturnStmt(self)

	class Var:
		def __init__(self, name, initializer):
			self.name = name
			self.initializer = initializer

		def accept(self, visitor):
			return visitor.visitVarStmt(self)

	class While:
		def __init__(self, condition, body):
			self.condition = condition
			self.body = body

		def accept(self, visitor):
			return visitor.visitWhileStmt(self)