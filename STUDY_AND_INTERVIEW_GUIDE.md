# 🎓 CogniCode: The Master 1-Day Study & Interview Guide

> **Your Complete Blueprint to Mastering CogniCode and LangGraph for the Infosys Specialist Programmer (SP / DSE) Interview.**

---

## 📅 The 1-Day Master Study Schedule

| Time | Focus Area | Goal |
| :--- | :--- | :--- |
| **09:00 - 10:30** | **LangGraph Core Architecture** | Understand `StateGraph`, `TypedDict`, `Nodes`, and `Conditional Edges`. |
| **10:30 - 12:00** | **Neuro-Symbolic AI & Memory** | Learn how Python AST works and how FAISS Episodic Memory provides few-shot guidance. |
| **12:00 - 13:30** | **Test-Driven Self-Healing Loop** | Master how the sandbox executes `pytest`, catches tracebacks, and self-repairs in a loop. |
| **14:30 - 16:00** | **Git & GitHub CI/CD Automation** | Understand automated branching, conventional commits, unified diffs, and Human-in-the-Loop. |
| **16:00 - 17:30** | **Hands-On UI Exploration** | Run `streamlit run app.py`, execute the 3 preset demos, and inspect the state tree. |
| **17:30 - 20:00** | **Mock Interview Drill** | Practice the 60-second pitch and memorize the answers to the Top 25 Questions below. |

---

## 🏛️ System Architecture Cheat Sheet (Draw This on Paper in Interview)

```
                            [User Input Code]
                                    │
                         [1. FAISS Episodic Memory]
                        (Retrieves known CWE patterns)
                                    │
                         [2. Symbolic AST Parser]
                       (Deterministic syntax check)
                                    │
                        ┌───────────┴───────────┐
                        ▼                       ▼
              [3. Security Agent]     [4. Big-O Profiler]
              (OWASP Top 10 / CWE)    (Time & Space Complexity)
                        └───────────┬───────────┘
                                    ▼
                     [5. Patch & Pytest Synthesizer]
                     (Generates fix + edge-case test)
                                    │
                                    ▼
                      [6. Pytest Execution Sandbox]
                                    │
                             ┌──────┴──────┐
                          (Pass)         (Fail & Retries < 3)
                             │              │
                             │              └──► [7. Self-Healing Reflection Node]
                             │                   (Reads error traceback & refactors)
                             │                            │
                             │                            └──► (Loops to Sandbox)
                             ▼
                 [8. Git Branch, Commit & PR Formulation]
                 (Unified diff, commit message, GitHub PR)
```

---

## 🧩 File-by-File Technical Deep Dive

### 1. `src/state.py` (The Single Source of Truth)
- **Concept:** In LangGraph, state is not scattered across global variables. It is maintained in a single strongly-typed Python dictionary (`TypedDict`).
- **Key Fields:**
  - `source_code`: The input code being evaluated.
  - `ast_analysis`: The deterministic findings from Python's compiler.
  - `retrieved_patterns`: Knowledge retrieved from the episodic memory bank.
  - `candidate_patch`: The remediated code draft.
  - `test_code`: The generated `pytest` verification suite.
  - `test_result`: Execution exit code, duration, stdout, and error traceback.
  - `retry_count`: Loop guard integer incremented on each self-healing cycle.
  - `node_history`: A running list tracking which nodes fired, used to illuminate the UI stepper.

### 2. `src/ast_analyzer.py` (Neuro-Symbolic AI)
- **Concept:** LLMs are stochastic (probabilistic) and frequently hallucinate syntax errors. **Symbolic AI** uses deterministic compilers to guarantee syntax correctness.
- **How it works:** We use Python’s standard `ast` (Abstract Syntax Tree) module.
- **What it checks:**
  - `ast.parse()`: Validates syntax before any test runs.
  - `ast.NodeVisitor`: Traverses the syntax tree to detect dangerous calls (`eval()`, `exec()`), recursive functions without base cases, and bare `except:` statements.
  - Computes **Cyclomatic Complexity** by counting decision branching nodes (`If`, `For`, `While`, `ExceptHandler`).

### 3. `src/memory.py` (Episodic Bug Memory Bank)
- **Concept:** Inspired by human episodic memory, the agent references an indexed bank of verified enterprise security and algorithmic patterns (CWE-89 SQLi, CWE-400 Exponential Recursion, CWE-798 Hardcoded Secrets, CWE-476 Null Dereference).
- **Why it matters:** Instead of guessing remediation patterns from zero context, the agent performs similarity retrieval to pull verified enterprise remediation templates.

### 4. `src/sandbox.py` (Sandboxed Pytest Execution)
- **Concept:** The agent cannot merely *claim* a bug is fixed—it must *prove* it through test-driven verification.
- **How it works:**
  - Creates an isolated `tempfile.TemporaryDirectory()`.
  - Writes `solution.py` and `test_solution.py`.
  - Spawns an isolated subprocess: `python -m pytest test_solution.py -v`.
  - Enforces a strict **10-second wall-clock timeout** to kill infinite loops or recursion bombs.
  - Captures `returncode` (0 = passed, non-zero = failed) and extracts the exact failure traceback.

### 5. `src/graph.py` (LangGraph Assembly & Conditional Routing)
- **Concept:** Linear chains (LangChain LCEL) are Directed Acyclic Graphs (DAGs) that cannot cycle backward. LangGraph introduces **cyclic state graphs**.
- **The Conditional Edge:**
  ```python
  def should_self_heal(state: AgentState):
      if state["test_result"]["passed"]:
          return "git_pr"
      if state["retry_count"] < state["max_retries"]:
          return "self_healing_reflection"
      return "git_pr"  # Max retries reached, escalate
  ```
- If the test fails, state routes into `self_healing_reflection`, where the LLM reads the compiler error traceback, repairs the code, and loops back into `sandbox_verifier`.

### 6. `src/git_manager.py` (Git & GitHub Automation)
- Generates standard unified diffs using Python's `difflib`.
- Formats institutional Pull Request Markdown descriptions with vulnerability summaries, Big-O tables, and test badges.
- Optionally calls the GitHub REST API (`POST /repos/{owner}/{repo}/pulls`) to open live PRs on GitHub.

---

## 🎯 Top 25 Infosys Interview Questions & Model Answers

### Category 1: LangGraph & Agentic Architecture

#### Q1: What is the core difference between LangChain and LangGraph?
> **Answer:** *"LangChain was designed for linear, directed acyclic graphs (DAGs)—where data flows strictly from prompt to LLM to output parser. However, real-world engineering workflows like code debugging require **loops, conditional branching, and persistence**. LangGraph extends LangChain by modeling workflows as stateful cyclic graphs with explicit state dictionaries (`TypedDict`), nodes as pure functions, and conditional edges that can loop back based on runtime conditions."*

#### Q2: How does LangGraph handle state management?
> **Answer:** *"In LangGraph, state is defined using a central schema (in our case, `AgentState`). Each node is a Python function that receives the current state and returns a dictionary of updated keys. LangGraph merges these updates into the central state. It also supports checkpointing via `MemorySaver` or databases to pause and resume workflows."*

#### Q3: How do you prevent infinite loops in cyclic agent graphs?
> **Answer:** *"We use two layers of protection: First, within the `AgentState`, we track an explicit counter `retry_count` and enforce `retry_count < max_retries` (bounded at 3) inside our conditional edge. Second, LangGraph allows passing a global `recursion_limit` parameter during compilation, which forcibly aborts execution if node transitions exceed a hard ceiling."*

#### Q4: What is Human-in-the-Loop (HITL) and how did you implement it?
> **Answer:** *"Human-in-the-Loop allows an agent to pause execution before performing an irreversible action (like deploying code or merging a PR). In LangGraph, this is achieved using `interrupt_before=['git_pr']`. The graph yields control to the UI, presents the side-by-side Git diff to the developer, and only resumes when the developer clicks 'Approve'."*

---

### Category 2: Neuro-Symbolic AI & Code Execution

#### Q5: What do you mean by 'Neuro-Symbolic AI' in this project?
> **Answer:** *"Generative AI models are neural and stochastic—meaning they excel at semantic creativity but often hallucinate syntax errors or invalid function calls. Symbolic AI uses deterministic rules and compilers. In CogniCode, I combined both: Python's native `ast` module acts as the symbolic parser, deterministically verifying syntax validity and extracting cyclomatic complexity, while LLMs provide the neural reasoning to analyze logic and generate refactored code."*

#### Q6: Why did you use Python AST instead of regular expressions (regex)?
> **Answer:** *"Regex is fragile and context-blind—it cannot reliably parse nested parentheses, multiline statements, or scope. An Abstract Syntax Tree (AST) parses code into a hierarchical grammatical tree, allowing us to inspect exact node types like `ast.FunctionDef`, `ast.Call`, and `ast.ExceptHandler` with 100% compiler-level accuracy."*

#### Q7: Isn't running LLM-generated code in a sandbox dangerous?
> **Answer:** *"Yes, executing arbitrary code is a major security risk. In CogniCode, we employ three safety layers:
> 1. **AST Pre-screening:** The code is inspected via AST to reject unauthorized built-ins like `os.system('rm -rf')`.
> 2. **Isolated Ephemeral Sandbox:** Code is executed in an isolated temporary directory using Python subprocesses.
> 3. **Wall-clock Timeouts:** Subprocesses are killed after 10 seconds to neutralize infinite loops or fork bombs."*

#### Q8: What happens if the LLM writes a 'tautological' test (e.g., `assert True`) just to pass?
> **Answer:** *"We use prompt guardrails that enforce test assertions to evaluate specific return values and boundary conditions against the imported function. Additionally, in our AST analysis, we inspect the generated test tree to verify that `assert` statements explicitly call the target function."*

---

### Category 3: Algorithmic Optimization & LeetCode Connection

#### Q9: How does the agent calculate Big-O complexity?
> **Answer:** *"The agent combines AST static metrics with LLM reasoning. Through the AST, we identify recursive call patterns without memoization, nested loop depths, and branching factors. The Algorithmic Profiler agent evaluates whether the recursion tree exhibits $O(2^N)$ binary branching, $O(N^2)$ quadratic traversal, or $O(N)$ linear scans, and recommends dynamic programming or memoization."*

#### Q10: Can you give an example of an algorithmic fix the agent performed?
> **Answer:** *"In our preset demo for Fibonacci, the naive code used binary recursion without caching, resulting in exponential $O(2^N)$ time complexity that hung on $N=35$. The agent diagnosed the recursion tree, applied an iterative dynamic programming loop, reduced time complexity to $O(N)$ and space to $O(1)$, and verified it with tests passing in 0.02 seconds."*

---

### Category 4: Security (OWASP & CWE)

#### Q11: What is CWE-89 and how does CogniCode remediate it?
> **Answer:** *"CWE-89 is SQL Injection. It occurs when user inputs are directly concatenated into SQL queries using f-strings or string formatting. CogniCode detects this flaw, references our Episodic Memory bank, and refactors the code to use parameterized queries with tuple placeholders (`?` or `%s`), preventing arbitrary SQL command execution."*

#### Q12: What is CWE-400?
> **Answer:** *"CWE-400 is Uncontrolled Resource Consumption. In software, this commonly manifests as exponential recursion, unindexed database queries, or unbounded memory allocations that can lead to denial-of-service (DoS). CogniCode identifies asymptotic bottlenecks and refactors them into optimal space/time algorithms."*

---

### Category 5: Git & Enterprise CI/CD Integration

#### Q13: How does CogniCode integrate with Git?
> **Answer:** *"Once the self-healing loop passes, CogniCode generates a standard unified diff using `difflib`. It automatically generates a feature branch name (e.g. `cognicode/fix-cwe89`), formulates a conventional commit message, and can call the GitHub REST API to raise a real Pull Request containing the full security audit and test execution logs."*

#### Q14: How would this fit into an enterprise company like Infosys?
> **Answer:** *"Infosys manages thousands of client codebases and recently launched the **Topaz Agentic Foundry** for SDLC optimization. CogniCode can be integrated as a GitHub Action or webhook into enterprise CI/CD pipelines. When a developer opens a PR, CogniCode automatically audits the code, suggests a verified fix with passing unit tests, and presents a PR for lead approval—saving hundreds of developer review hours."*

---

### Category 6: Token Economics & Cost Optimization

#### Q15: In an enterprise setting, how do you prevent LLM API costs from exploding?
> **Answer:** *"In CogniCode, we implemented a dual-layer cost-reduction system:
> 1. **AST-Hash Semantic Caching (`src/cache.py`):** Before making any LLM call, we compute a normalized SHA-256 fingerprint of the code structure. If duplicate or functionally identical code is audited, we trigger a cache-hit conditional edge in LangGraph, immediately bypassing all LLM nodes and routing directly to verification/PR generation. This achieves **100% token savings ($0 cost) and 0-second latency**.
> 2. **Deterministic Pre-Filtering & Prompt Pruning:** Instead of passing entire large codebases to the LLM, our symbolic AST analyzer extracts only relevant function signatures, dangerous calls, and cyclomatic complexity numbers, drastically compressing input prompt tokens.
> 3. **Real-Time Cost Telemetry (`src/cost_tracker.py`):** We track prompt and completion tokens for every run, computing exact dollar expenditures based on enterprise pricing ($0.15/$0.60 per 1M tokens) and quantifying financial savings."*

#### Q16: Why use AST hashing instead of standard string hashing for the cache?
> **Answer:** *"Simple string hashing is brittle—adding a comment, extra whitespace, or changing variable formatting will cause a cache miss. By normalizing whitespace, stripping comment lines, and keying off the AST structural representation, we ensure that cosmetic code edits still hit the cache, maximizing token efficiency across teams."*

---

### Category 7: Graphify & Long-Horizon Knowledge Graph Memory

#### Q17: What is Graphify and why did you incorporate it into CogniCode?
> **Answer:** *"Graphify (`Graphify-Labs/graphify`) is a cutting-edge paradigm for AI agent persistent memory. When building complex agentic systems, AI context windows eventually expire or run out of tokens. Standard agents waste thousands of tokens sequentially reading every file in a repository to understand relationships.
> 
> Inspired by Graphify, we built `graphify_engine.py` which uses Python's native AST parser to deterministically extract our codebase into a **queryable knowledge graph** with 95 nodes and 617 edges:
> - `graph.json`: Machine-readable graph of modules, classes, functions, LangGraph nodes, prompts, and state schemas.
> - `GRAPH_REPORT.md`: Architectural summary identifying high-connectivity **'God Nodes'** (e.g. `AgentState`, `cognicode_graph`, `git_pr_node`) and an **AI Agent Bootstrap Prompt**.
> - `graph.html`: Standalone, interactive network visualization embedded directly in our Streamlit UI.
> 
> If an agent session dies or tokens expire, any future AI assistant (Claude, Cursor, Antigravity) can ingest this single graph memory file and instantly achieve 100% architectural comprehension with zero redundant file reading."*

#### Q18: What are 'God Nodes' in a codebase knowledge graph?
> **Answer:** *"In network graph theory applied to codebases, God Nodes are entities with exceptionally high total degree centrality (many incoming and outgoing dependencies). In CogniCode, our primary God Node is `AgentState` in `src/state.py` (which acts as the single source of truth passed across all 8 nodes) and `git_pr_node` (which aggregates reports from security, complexity, pytest, and cost tracking). Identifying God Nodes helps developers immediately locate critical architectural bottlenecks and regression risks."*

---

## 📝 Resume Bullet Points (Copy & Paste to Your Resume)

Replace or upgrade your current projects with this:

**CogniCode — Autonomous Multi-Agent Code Remediation & Self-Healing Engine**  
*Python, LangGraph, LangChain, FAISS, Pytest, Python AST, Graphify Knowledge Graph, Git/GitHub REST API, Streamlit*  
- Engineered an autonomous multi-agent code remediation and self-healing platform using **LangGraph** to detect OWASP/CWE vulnerabilities, optimize algorithmic Big-O bottlenecks, and formulate institutional Pull Requests.
- Implemented a **Neuro-Symbolic architecture** combining deterministic Python **AST parsing** for syntax/complexity verification with specialized LLM reasoning agents and a **FAISS Episodic Bug Memory Bank**.
- Developed a **cyclic self-healing reflection loop** running in an isolated **Pytest sandbox**, autonomously diagnosing execution stack traces and repairing code until test suites achieve 100% pass rates.
- Architected an enterprise **AST-Hash Semantic Cache** and **Token Cost Telemetry Engine** (`gpt-4o-mini`), bypassing LLM nodes on duplicate submissions to achieve **100% token cost savings ($0 spend) and 0s latency**.
- Designed a **Graphify Codebase Knowledge Graph Memory** (`graphify_engine.py`), mapping 95 code entities and 617 dependency edges to enable instant long-horizon AI agent state bootstrapping and interactive network visualization.
- Automated end-to-end Git CI/CD workflows, generating unified diffs, conventional commits, and live **GitHub Pull Requests** with automated test-execution badges.

