import os
import sys
import time
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv("C:/Users/Yashvardhan Singh/.gemini/antigravity/scratch/cognicode-engine/.env")

from src.config import get_llm
from src.nodes import set_runtime_llm
from src.graph import cognicode_graph

code = """import sqlite3

def detect_fraudulent_pair(transactions: list, target_anomaly: int, account_id: str) -> list:
    n = len(transactions)
    matched_pair = []
    for i in range(n):
        for j in range(i + 1, n):
            if transactions[i] + transactions[j] == target_anomaly:
                matched_pair = [transactions[i], transactions[j]]
                break
        if matched_pair:
            break

    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO audit (account, anomaly) VALUES ('{account_id}', '{target_anomaly}')")
    conn.close()

    return matched_pair
"""

llm = get_llm("openai", "gpt-4o-mini")
set_runtime_llm(llm)

state = {
    "source_code": code,
    "filename": "solution.py",
    "language": "python",
    "ast_analysis": {},
    "retrieved_patterns": [],
    "security_report": {},
    "complexity_report": {},
    "quality_report": {},
    "candidate_patch": code,
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
    "node_history": [],
    "cache_hit": False,
    "cost_metrics": {}
}

print("=== RUN 1: FRESH AUDIT (Cache Miss) ===")
t0 = time.time()
res1 = cognicode_graph.invoke(state)
t1 = time.time()
print(f"Time Taken: {t1 - t0:.2f}s")
print("Cache Hit:", res1.get("cache_hit"))
print("Cost Metrics:", res1.get("cost_metrics"))
print("Node History:", res1.get("node_history"))

print("\n=== RUN 2: REPEAT AUDIT (Cache Hit - 100% Token Savings) ===")
t2 = time.time()
res2 = cognicode_graph.invoke(state)
t3 = time.time()
print(f"Time Taken: {t3 - t2:.3f}s (Instant!)")
print("Cache Hit:", res2.get("cache_hit"))
print("Cost Metrics:", res2.get("cost_metrics"))
print("Node History:", res2.get("node_history"))

