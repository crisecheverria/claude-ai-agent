# Understanding Factorial

A factorial is the product of all positive integers less than or equal to a given positive integer. It is denoted by the symbol '!'.

## Definition
The factorial of a non-negative integer n, denoted as n!, is the product of all positive integers less than or equal to n.

## Formula
n! = n × (n-1) × (n-2) × ... × 3 × 2 × 1

## Examples
- 5! = 5 × 4 × 3 × 2 × 1 = 120
- 4! = 4 × 3 × 2 × 1 = 24
- 3! = 3 × 2 × 1 = 6
- 2! = 2 × 1 = 2
- 1! = 1
- 0! = 1 (by definition)

## Special Cases
- 0! is defined as 1
- Factorial is only defined for non-negative integers
- Factorial grows very quickly (10! is already 3,628,800)

## Simple Python Implementation
```python
def factorial(n):
    if n < 0:
        return "Factorial is not defined for negative numbers"
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```

## Real-world Applications
- Probability and statistics
- Combinatorics
- Permutations and combinations
- Scientific calculations