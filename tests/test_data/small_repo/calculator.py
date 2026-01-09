"""
Simple calculator module for testing documentation generation.
"""


def add(a: int, b: int) -> int:
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


def multiply(a: int, b: int) -> int:
    return a * b


def divide(a: float, b: float) -> float:
    """
    Divide a by b.
    
    Args:
        a: Numerator
        b: Denominator
        
    Returns:
        Result of division
        
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize calculator with zero result."""
        self.result = 0
    
    def add(self, value: float) -> float:
        """Add value to current result."""
        self.result += value
        return self.result
    
    def subtract(self, value: float) -> float:
        """Subtract value from current result."""
        self.result -= value
        return self.result
    
    def reset(self) -> None:
        """Reset result to zero."""
        self.result = 0
    
    def get_result(self) -> float:
        """Get current result."""
        return self.result


if __name__ == "__main__":
    # Test the calculator
    calc = Calculator()
    calc.add(10)
    calc.subtract(5)
    print(f"Result: {calc.get_result()}")  # Should print 5
