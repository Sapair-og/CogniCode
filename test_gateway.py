import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

from src.gateway import llm_gateway

def test_gateway_health():
    print("--- Testing Enterprise LLM Gateway ---")
    health = llm_gateway.get_gateway_health()
    print("Gateway Health:", health)
    assert "status" in health
    assert "primary_route" in health
    assert "fallback_route" in health
    print(" Gateway Health verified successfully!")

def test_resilient_llm():
    llm = llm_gateway.get_resilient_llm()
    assert llm is not None
    print(" Resilient LLM resolution verified successfully!")

if __name__ == "__main__":
    test_gateway_health()
    test_resilient_llm()
    print("\n All Enterprise LLM Gateway Tests Passed!")
