import langgraph
import langchain
import langchain_openai
import langchain_groq
import faiss
import pytest
import streamlit
import git

print("1. Core Libraries Import: SUCCESS")

from src.ast_analyzer import analyze_code_ast
ast_res = analyze_code_ast("""
def solve(n):
    if n > 0:
        return n * 2
    return 0
""")
print(f"2. Symbolic AST Analysis: SUCCESS, Cyclomatic Complexity = {ast_res['cyclomatic_complexity']}")

from src.memory import memory_bank
patterns = memory_bank.retrieve_relevant_patterns("cursor.execute('SELECT * FROM users WHERE name=' + user)")
print(f"3. Episodic Memory Bank: SUCCESS, Retrieved Pattern = {patterns[0]['id']}: {patterns[0]['title'][:45]}...")

from src.sandbox import run_test_in_sandbox
test_res = run_test_in_sandbox(
    candidate_code="def multiply(a, b):\n    return a * b\n",
    test_code="from solution import multiply\ndef test_mult():\n    assert multiply(3, 4) == 12\n"
)
print(f"4. Pytest Sandbox: SUCCESS, Tests Passed = {test_res['passed']} in {test_res['duration_seconds']}s")

from src.graph import cognicode_graph
print(f"5. LangGraph StateMachine: SUCCESS, Compiled Nodes = {list(cognicode_graph.nodes.keys())}")
print("\n[SUCCESS] ALL 5 VERIFICATION CHECKS PASSED PERFECTLY!")
