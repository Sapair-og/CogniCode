import os
import sys
import json
import time

# Add root directory to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

from src.cache import CodeAuditCache
from src.cost_tracker import calculate_workflow_cost, estimate_tokens
from src.graph import cognicode_graph
from src.state import AgentState

def test_cache_mechanism():
    print("--- 1. Testing CodeAuditCache ---")
    cache = CodeAuditCache()
    sample_code = "def add(a, b):\n    # A comment\n    return a + b\n"
    
    # Store dummy result
    dummy_result = {
        "security_report": {"cwe_id": "CWE-None", "severity": "LOW"},
        "complexity_report": {"time_before": "O(1)", "time_after": "O(1)"},
        "candidate_patch": sample_code,
        "test_code": "def test_add(): assert add(1, 2) == 3",
        "test_result": {"passed": True},
        "git_diff": "",
        "pr_title": "fix: add function",
        "pr_body": "PR Body"
    }
    
    cache.put(sample_code, "gpt-4o-mini", dummy_result)
    retrieved = cache.get(sample_code, "gpt-4o-mini")
    assert retrieved is not None, "Cache should return stored result"
    assert retrieved["security_report"]["cwe_id"] == "CWE-None"
    print(" CodeAuditCache put and get verified successfully!")

def test_cost_tracker():
    print("\n--- 2. Testing Cost Tracker ---")
    input_text = "def compute(): return 42" * 50
    output_text = "def compute(): return 42 # optimized" * 50
    
    # Fresh run
    fresh_cost = calculate_workflow_cost(input_text, output_text, model_name="gpt-4o-mini", is_cached=False)
    assert fresh_cost["total_tokens"] > 0
    assert fresh_cost["cost_usd"] > 0
    assert fresh_cost["cached"] is False
    print(f" Fresh Run Cost: {fresh_cost['total_tokens']} tokens, ${fresh_cost['cost_usd']:.6f} USD")
    
    # Cached run
    cached_cost = calculate_workflow_cost(input_text, output_text, model_name="gpt-4o-mini", is_cached=True)
    assert cached_cost["total_tokens"] == 0
    assert cached_cost["cost_usd"] == 0.0
    assert cached_cost["cached"] is True
    assert cached_cost["savings_usd"] > 0
    print(f" Cached Run: 0 tokens billed, $0.00 cost, Savings: ${cached_cost['savings_usd']:.6f} USD")

if __name__ == "__main__":
    test_cache_mechanism()
    test_cost_tracker()
    print("\n All Cache and Cost Tracking Unit Tests Passed!")
