class TrevorsCalculator:
    """A simple calculator class to perform basic arithmetic operations."""

    def add(self, a, b):
        """Returns the sum of a and b."""
        return a + b

    def subtract(self, a, b):
        """Returns the difference of a and b."""
        return a - b

    def multiply(self, a, b):
        """Returns the product of a and b."""
        return a * b

    def divide(self, a, b):
        """Returns the quotient of a and b. Raises ValueError for division by zero."""
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

def main():
    """Main function to demonstrate the TrevorsCalculator class."""
    calc = TrevorsCalculator()
    
    # Demonstrating the calculator operations
    print("Addition (2 + 3):", calc.add(2, 3))
    print("Subtraction (5 - 2):", calc.subtract(5, 2))
    print("Multiplication (3 * 4):", calc.multiply(3, 4))
    print("Division (10 / 2):", calc.divide(10, 2))
    
    try:
        print("Division (10 / 0):", calc.divide(10, 0))
    except ValueError as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
