# CogniCode Knowledge Graph Architecture & Memory Report
*Generated deterministically by CogniCode-Graphify-Engine (inspired by Graphify-Labs/graphify)*

---

## 🤖 AI Agent Bootstrap & Memory Injection Prompt
> **Copy-paste this prompt into any AI agent session** (Claude, Cursor, ChatGPT, or Antigravity) when your context expires to instantly resume development without re-reading source files:

```markdown
You are working on CogniCode, an enterprise Autonomous Multi-Agent Code Remediation & Self-Healing Engine.
Here is the complete architectural knowledge graph and mental model:

1. State Contract (Single Source of Truth):
   - `src/state.py` -> `AgentState` (TypedDict holding source_code, ast_analysis, retrieved_patterns, security_report, complexity_report, candidate_patch, test_code, test_result, retry_count, git_diff, git_branch, pr_title, pr_body, cache_hit, cost_metrics).
2. LangGraph Stateful Workflow (`src/graph.py`):
   - Flow: START -> retrieve_memory -> symbolic_ast -> [check_cache_bypass: if cache_hit -> git_pr] -> security_audit -> complexity_profiler -> patch_synthesizer -> sandbox_verifier -> [should_self_heal: if fail & retries < max -> self_healing_reflection -> sandbox_verifier; if pass -> git_pr] -> END.
3. Component Layer:
   - `src/cache.py`: `CodeAuditCache` with SHA-256 AST hashing in `.cache/audit_cache.json`.
   - `src/cost_tracker.py`: Token estimator & cost metrics ($0.15/$0.60 per 1M tokens).
   - `src/memory.py`: FAISS episodic vector bank seeded with CWE-89, CWE-400, CWE-476, etc.
   - `src/ast_analyzer.py`: Python AST visitor calculating cyclomatic complexity & detecting dangerous calls.
   - `src/sandbox.py`: Subprocess Pytest runner with timeout protection.
   - `src/git_manager.py`: Git branch manager, unified diff builder, and GitHub REST API integration.
   - `src/chains.py`: Pydantic structured output models & LLM prompt templates.
   - `app.py`: Streamlit reactive UI with cost metrics, git diff viewer, and embedded interactive graph.

You are now 100% synchronized with the CogniCode repository architecture. Await user instruction.
```

---

## 📊 Graph Summary Statistics
- **Total Entities (Nodes):** 106
- **Total Relationships (Edges):** 742
- **Node Breakdown:**
  - **Class:** 10
  - **Function:** 43
  - **Langgraph Node:** 10
  - **Module:** 15
  - **Prompt:** 4
  - **State Key:** 20
  - **Test Sample:** 3
  - **Ui:** 1

---

## 👑 Central Architectural Hubs ("God Nodes")
These nodes have the highest connectivity and form the backbone of the system:

| Node ID | Category | Total Degree | In-Degree | Out-Degree | Role / File |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `git_pr_node()` | `langgraph_node` | **75** | 3 | 72 | `src/nodes.py` |
| `symbolic_ast_node()` | `langgraph_node` | **47** | 2 | 45 | `src/nodes.py` |
| `TypeSafeJevClient.triage_code()` | `function` | **42** | 1 | 41 | `src/jev_client.py` |
| `run_test_in_sandbox()` | `function` | **42** | 1 | 41 | `src/sandbox.py` |
| `create_github_pull_request()` | `function` | **31** | 1 | 30 | `src/git_manager.py` |
| `self_healing_reflection_node()` | `langgraph_node` | **31** | 2 | 29 | `src/nodes.py` |
| `analyze_code_ast()` | `function` | **28** | 1 | 27 | `src/ast_analyzer.py` |
| `src/nodes.py` | `module` | **27** | 2 | 25 | `src/nodes.py` |
| `security_audit_node()` | `langgraph_node` | **27** | 2 | 25 | `src/nodes.py` |
| `patch_synthesizer_node()` | `langgraph_node` | **26** | 2 | 24 | `src/nodes.py` |

---

## 🔄 Stateful LangGraph Node Pipeline

```mermaid
graph TD
    START([START]) --> M1[1. retrieve_memory_node]
    M1 --> M2[2. symbolic_ast_node]
    M2 -->|Cache Hit (100% Token Savings)| M8[8. git_pr_node]
    M2 -->|Cache Miss| M3[3. security_audit_node]
    M3 --> M4[4. complexity_profiler_node]
    M4 --> M5[5. patch_synthesizer_node]
    M5 --> M6[6. sandbox_verifier_node]
    M6 -->|Tests Passed| M8
    M6 -->|Tests Failed & Retries < 3| M7[7. self_healing_reflection_node]
    M7 --> M6
    M8 --> END([END: Verified PR & Diff])
```

---

## 📁 Module Inventory
- **`app.py`**: Core module component
- **`run_demo_test.py`**: Core module component
- **`src/__init__.py`**: CogniCode Engine
Autonomous Multi-Agent Code Remediation & Test-Driven Self-Healing Engine.
- **`src/ast_analyzer.py`**: Core module component
- **`src/cache.py`**: Core module component
- **`src/chains.py`**: Core module component
- **`src/config.py`**: Core module component
- **`src/cost_tracker.py`**: Core module component
- **`src/gateway.py`**: Enterprise LLM Gateway for CogniCode
====================================
Provides unified routing, automatic failover (OpenAI -> Groq),
latency telemetry, and circuit-breaking for multi-provider resilience.
- **`src/git_manager.py`**: Core module component
- **`src/graph.py`**: Core module component
- **`src/jev_client.py`**: TypeSafe AI Jev Client
======================
Integrates Jev ("System One" decision model by TypeSafe AI) into CogniCode.
Provides sub-second, typed, and calibrated evaluations (Noul, Choice, Score)
to triage code before or alongside heavier generative LLMs (System Two).
- **`src/memory.py`**: Core module component
- **`src/nodes.py`**: Core module component
- **`src/sandbox.py`**: Core module component
- **`src/state.py`**: Core module component
