import os
from dotenv import load_dotenv
from src.config import get_llm
from src.nodes import set_runtime_llm
from src.graph import cognicode_graph
from src.state import AgentState

load_dotenv("C:/Users/Yashvardhan Singh/.gemini/antigravity/scratch/cognicode-engine/.env")

# Sample SQL Injection code
with open("samples/sql_injection.py", "r") as f:
    sample_code = f.read()

print("[TEST] Initializing CogniCode multi-agent graph with OpenAI gpt-4o-mini...")
llm = get_llm(provider="openai", model_name="gpt-4o-mini")
set_runtime_llm(llm)

initial_state: AgentState = {
    "source_code": sample_code,
    "filename": "solution.py",
    "language": "python",
    "ast_analysis": {},
    "retrieved_patterns": [],
    "security_report": {},
    "complexity_report": {},
    "quality_report": {},
    "candidate_patch": sample_code,
    "test_code": "",
    "test_result": {},
    "retry_count": 0,
    "max_retries": 3,
    "git_branch": "",
    "git_diff": "",
    "commit_message": "",
    "pr_title": "",
    "pr_body": "",
    "pr_url": None,
    "status": "analyzing",
    "node_history": []
}

print("[TEST] Invoking LangGraph workflow...")
final_state = cognicode_graph.invoke(initial_state)

print("\n=== COGNICODE RUN COMPLETE ===")
print("Workflow Status:", final_state.get("status"))
print("Security CWE:", final_state.get("security_report", {}).get("cwe_id"))
print("Severity:", final_state.get("security_report", {}).get("severity"))
print("Pytest Passed:", final_state.get("test_result", {}).get("passed"))
print("Execution History:")
for step in final_state.get("node_history", []):
    print("  *", step)
print("\nGenerated Git Branch:", final_state.get("git_branch"))
print("Generated PR Title:", final_state.get("pr_title"))
