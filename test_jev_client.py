import os
import sys

# Ensure UTF-8 console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.jev_client import TypeSafeJevClient

def test_jev_triage():
    print("--- Testing TypeSafe AI Jev System-One Triage ---")
    client = TypeSafeJevClient()

    # 1. SQL Injection Test
    sqli_code = "cursor.execute(f\"SELECT * FROM users WHERE user='{user}' AND pass='{password}'\")"
    res1 = client.triage_code(sqli_code)
    print("SQLi Result:", res1["cwe_choice"], f"(Risk: {res1['risk_score']}/10, Latency: {res1['latency_ms']}ms)")
    assert res1["has_vulnerability"] is True
    assert res1["cwe_choice"] == "CWE-89"
    assert res1["risk_score"] >= 8

    # 2. Exponential Recursion Test
    fib_code = """
def compute_nth_fibonacci(n: int) -> int:
    if n <= 1: return n
    return compute_nth_fibonacci(n - 1) + compute_nth_fibonacci(n - 2)
"""
    res2 = client.triage_code(fib_code)
    print("Fibonacci Result:", res2["cwe_choice"], f"(Complexity: {res2['complexity_choice']}, Latency: {res2['latency_ms']}ms)")
    assert res2["has_vulnerability"] is True
    assert res2["cwe_choice"] == "CWE-400"
    assert res2["complexity_choice"] == "O(2^N)"

    # 3. Clean Code Test
    clean_code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    res3 = client.triage_code(clean_code)
    print("Clean Code Result:", res3["cwe_choice"], f"(Vulnerable: {res3['has_vulnerability']}, Latency: {res3['latency_ms']}ms)")
    assert res3["has_vulnerability"] is False
    assert res3["risk_score"] <= 3

    print("\n All TypeSafe AI Jev System-One Tests Passed Successfully!")

if __name__ == "__main__":
    test_jev_triage()
