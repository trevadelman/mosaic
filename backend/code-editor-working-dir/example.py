"""
Example Python file for testing the code editor agent. Trevor

This file contains a simple Python function to calculate Fibonacci numbers using memoization.
"""

def fibonacci(n, memo=None):
    """
    Calculate the nth Fibonacci number using memoization.
    
    Args:
        n (int): The position in the Fibonacci sequence (0-indexed).
    
    Returns:
        int: The nth Fibonacci number.
    """
    if memo is None:
        memo = {}
    
    if n < 0:
        raise ValueError("Input should be a non-negative integer.")
    
    if n in memo:
        return memo[n]

    if n <= 1:
        return n

    # Store the computed Fibonacci numbers in the memo dictionary
    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]

def main():
    """Main function to demonstrate the Fibonacci function."""
    # Print the first 10 Fibonacci numbers
    print("First 10 Fibonacci numbers:")
    for i in range(10):
        print(f"fibonacci({i}) = {fibonacci(i)}")

if __name__ == "__main__":
    main()