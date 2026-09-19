def compute_nth_fibonacci(n: int) -> int:
    """
    Computes the N-th Fibonacci number.
    PERFORMANCE BOTTLENECK: Naive binary recursion produces O(2^N) exponential time complexity,
    leading to severe CPU starvation and stack overflow on N >= 35 (CWE-400).
    """
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    if n == 0:
        return 0
    elif n == 1:
        return 1
    
    # Exponential recursive calls without memoization or dynamic programming
    return compute_nth_fibonacci(n - 1) + compute_nth_fibonacci(n - 2)
