class anyClass:
    def __init__(self):
        self.field = 1

a = anyClass()
b = a
b.field = 2
print(a.field)