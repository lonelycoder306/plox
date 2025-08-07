# Example of overloading operators in Python for a class.

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        # Overload the '+' operator for Vector objects
        return Vector(self.x + other.x, self.y + other.y)

    def __str__(self):
        # Overload the str() function for Vector objects
        return f"Vector({self.x}, {self.y})"

# Create Vector objects
v1 = Vector(1, 2)
v2 = Vector(3, 4)

# Use the overloaded '+' operator
v3 = v1 + v2
print(v3) # Output: Vector(4, 6)