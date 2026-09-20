import os
import sys
import time
import json
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

import streamlit as st

# Configure Streamlit Page
st.set_page_config(
    page_title="CogniCode | Autonomous Multi-Agent Code Remediation",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E88E5, #7E57C2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #757575;
        margin-bottom: 1.5rem;
    }
    .metric-box {
        background-color: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .metric-box h4 {
        margin-top: 0;
        margin-bottom: 10px;
    }
    .metric-box p {
        margin-bottom: 6px;
    }
    .badge-critical { background-color: #b71c1c; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .badge-high { background-color: #e65100; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .badge-safe { background-color: #1b5e20; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .node-active {
        padding: 8px 14px;
        background-color: rgba(30, 136, 229, 0.15);
        border-left: 4px solid #1e88e5;
        border-radius: 4px;
        margin-bottom: 6px;
        font-family: monospace;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# App Title
st.markdown('<div class="main-header">🛡️ CogniCode Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Multi-Agent Code Remediation & Test-Driven Self-Healing (LangGraph • Symbolic AST • FAISS Memory • GitHub)</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Agent & Model Controls")
    
    provider = st.selectbox(
        "LLM Provider",
        ["OpenAI", "Groq"],
        index=0,
        help="Select OpenAI (gpt-4o-mini) or Groq (llama-3.3-70b-versatile)"
    )
    
    if provider == "OpenAI":
        env_openai_key = os.getenv("OPENAI_API_KEY", "")
        api_key_input = st.text_input(
            "OpenAI API Key",
            value=env_openai_key,
            type="password",
            help="Your OpenAI API Key. Loaded automatically from .env."
        )
        if env_openai_key:
            st.caption("✅ Loaded from `.env`")
        selected_model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    else:
        env_groq_key = os.getenv("GROQ_API_KEY", "")
        api_key_input = st.text_input(
            "Groq API Key",
            value=env_groq_key,
            type="password",
            help="Your Groq API Key. Loaded automatically from .env."
        )
        if env_groq_key:
            st.caption("✅ Loaded from `.env`")
        selected_model = st.selectbox("Model", ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"], index=0)
        
    max_retries = st.slider("Max Self-Healing Retries", min_value=1, max_value=5, value=3)
    
    st.markdown("---")
    st.subheader("🐙 GitHub Integration")
    env_gh_token = os.getenv("GITHUB_TOKEN", "")
    github_token = st.text_input(
        "GitHub Token (Optional)",
        value=env_gh_token,
        type="password",
        help="Personal Access Token to open live PRs. Loaded automatically from .env."
    )
    if env_gh_token:
        st.caption("✅ Loaded from `.env`")
        
    env_gh_repo = os.getenv("GITHUB_REPOSITORY", "")
    github_repo = st.text_input(
        "GitHub Repo (e.g. user/repo)",
        value=env_gh_repo,
        placeholder="Sapair-og/CogniCode"
    )
    if env_gh_repo:
        st.caption(f"✅ Target repo: `{env_gh_repo}`")
    
    st.markdown("---")
    st.markdown("""
    **Architecture Highlights:**
    - 🔍 **Symbolic AST:** Deterministic Python parser
    - 🧠 **Episodic Memory:** FAISS CWE/OWASP patterns
    - 🧪 **Sandbox:** Isolated Pytest runner
    - 🔄 **Cyclic Graph:** Self-healing reflection loop
    - ⚡ **AST Cache:** 100% token savings on repeat runs
    - 🕸️ **Graphify:** Queryable graphical codebase memory
    """)
    
    st.markdown("---")
    st.subheader("🕸️ Project Graph Memory")
    st.caption("Explore repository architecture & dependencies.")
    show_graph_standalone = st.checkbox("Show Interactive Graph", value=False)

# Load Presets
PRESETS = {
    "CWE-89: SQL Injection Vulnerability": (
        "import sqlite3\n\n"
        "def authenticate_user(username: str, password_hash: str) -> dict:\n"
        "    \"\"\"\n"
        "    VULNERABILITY: Raw string interpolation enables SQL Injection (CWE-89).\n"
        "    \"\"\"\n"
        "    conn = sqlite3.connect(':memory:')\n"
        "    cursor = conn.cursor()\n"
        "    query = f\"SELECT id, username, role FROM users WHERE username = '{username}' AND password = '{password_hash}'\"\n"
        "    cursor.execute(query)\n"
        "    row = cursor.fetchone()\n"
        "    conn.close()\n"
        "    if row:\n"
        "        return {'id': row[0], 'username': row[1], 'role': row[2]}\n"
        "    return None\n"
    ),
    "CWE-400: Exponential O(2^N) Algorithmic Bottleneck": (
        "def compute_nth_fibonacci(n: int) -> int:\n"
        "    \"\"\"\n"
        "    PERFORMANCE BOTTLENECK: Binary recursion with O(2^N) time complexity (CWE-400).\n"
        "    \"\"\"\n"
        "    if n < 0:\n"
        "        raise ValueError('Must be non-negative')\n"
        "    if n <= 1:\n"
        "        return n\n"
        "    return compute_nth_fibonacci(n - 1) + compute_nth_fibonacci(n - 2)\n"
    ),
    "Hybrid: O(N^2) Two-Sum Bottleneck + CWE-89 SQLi": (
        "import sqlite3\n\n"
        "def detect_fraudulent_pair(transactions: list, target_anomaly: int, account_id: str) -> list:\n"
        "    \"\"\"\n"
        "    1. ALGORITHM BOTTLENECK: Brute-force nested loops O(N^2) search.\n"
        "    2. SECURITY VULNERABILITY: Raw SQL string formatting (CWE-89 SQLi).\n"
        "    \"\"\"\n"
        "    n = len(transactions)\n"
        "    matched_pair = []\n"
        "    for i in range(n):\n"
        "        for j in range(i + 1, n):\n"
        "            if transactions[i] + transactions[j] == target_anomaly:\n"
        "                matched_pair = [transactions[i], transactions[j]]\n"
        "                break\n"
        "        if matched_pair:\n"
        "            break\n\n"
        "    # Insecure query execution\n"
        "    conn = sqlite3.connect(':memory:')\n"
        "    cursor = conn.cursor()\n"
        "    cursor.execute(f\"INSERT INTO audit (account, anomaly) VALUES ('{account_id}', '{target_anomaly}')\")\n"
        "    conn.close()\n\n"
        "    return matched_pair\n"
    ),
    "CWE-476: NoneType Null Pointer Crash": (
        "def extract_user_contact_info(payload: dict) -> str:\n"
        "    \"\"\"\n"
        "    VULNERABILITY: Chained access without null safety causes fatal NoneType crash (CWE-476).\n"
        "    \"\"\"\n"
        "    user = payload['user']\n"
        "    profile = user['profile']\n"
        "    contacts = profile['contacts']\n"
        "    secondary_email = contacts['secondary_email']\n"
        "    return secondary_email.strip().lower()\n"
    ),
    "Custom Python Input": ""
}

# Main Workspace
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📝 Input Source Code")
    preset_choice = st.selectbox("Select Preset Demo or Custom", list(PRESETS.keys()))
    
    default_code = PRESETS[preset_choice] if preset_choice != "Custom Python Input" else "def example():\n    pass\n"
    code_input = st.text_area(
        "Source Code to Remediate",
        value=default_code,
        height=320,
        help="Paste any Python function to analyze and remediate."
    )
    
    run_btn = st.button("🚀 Run Autonomous Remediation", type="primary", use_container_width=True)

with col_right:
    st.subheader("⚡ Live Multi-Agent Execution Visualizer")
    status_placeholder = st.empty()
    progress_bar = st.empty()
    steps_container = st.container()

# Standalone Graph Viewer (if toggled before running)
if show_graph_standalone and "cognicode_result" not in st.session_state and not run_btn:
    st.markdown("---")
    st.subheader("🕸️ Project Knowledge Graph (Graphify Memory)")
    st.caption("Interactive queryable architecture map of all modules, classes, functions, and state dependencies.")
    graph_html_path = os.path.join(os.path.dirname(__file__), "graphify-out", "graph.html")
    if os.path.exists(graph_html_path):
        with open(graph_html_path, "r", encoding="utf-8") as f:
            html_data = f.read()
        import streamlit.components.v1 as components
        components.html(html_data, height=720, scrolling=True)

# Execution Logic
if run_btn:
    effective_key = (api_key_input or "").strip() or (os.getenv("OPENAI_API_KEY", "") if provider == "OpenAI" else os.getenv("GROQ_API_KEY", ""))
    if not effective_key:
        st.error(f"Please provide an API key for {provider} in the sidebar or in your .env file.")
    elif not code_input.strip():
        st.warning("Please provide Python source code to analyze.")
    else:
        # Configure runtime environment
        if provider == "OpenAI":
            os.environ["OPENAI_API_KEY"] = effective_key
        else:
            os.environ["GROQ_API_KEY"] = effective_key
            
        from src.config import get_llm
        from src.nodes import set_runtime_llm
        from src.graph import cognicode_graph
        from src.state import AgentState
        
        try:
            runtime_llm = get_llm(
                provider=provider.lower(),
                model_name=selected_model,
                api_key=effective_key,
                temperature=0.1
            )
            set_runtime_llm(runtime_llm)
        except Exception as e:
            st.error(f"Failed to initialize LLM: {str(e)}")
            st.stop()
            
        # Initialize State
        initial_state: AgentState = {
            "source_code": code_input,
            "filename": "solution.py",
            "language": "python",
            "ast_analysis": {},
            "retrieved_patterns": [],
            "security_report": {},
            "complexity_report": {},
            "quality_report": {},
            "candidate_patch": code_input,
            "test_code": "",
            "test_result": {},
            "retry_count": 0,
            "max_retries": max_retries,
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
        
        status_placeholder.info("⏳ Initializing CogniCode state machine...")
        progress_bar.progress(10)
        
        # Stream or invoke graph
        with st.spinner("Multi-Agent team is analyzing, synthesizing tests, and running sandbox..."):
            final_state = cognicode_graph.invoke(initial_state)
            
        progress_bar.progress(100)
        status_placeholder.success(f"✨ Workflow Complete! Status: {final_state.get('status', 'verified').upper()}")
        
        # Display Execution History in right column
        with steps_container:
            for step in final_state.get("node_history", []):
                st.markdown(f'<div class="node-active">✓ {step}</div>', unsafe_allow_html=True)
                
        # Store in session state for results tab rendering
        st.session_state["cognicode_result"] = final_state

# Display Results Section if Available
if "cognicode_result" in st.session_state:
    res = st.session_state["cognicode_result"]
    sec = res.get("security_report", {})
    if isinstance(sec, list):
        sec = sec[0] if len(sec) > 0 else {}
    elif not isinstance(sec, dict):
        sec = {}

    comp = res.get("complexity_report", {})
    if isinstance(comp, list):
        comp = comp[0] if len(comp) > 0 else {}
    elif not isinstance(comp, dict):
        comp = {}

    test = res.get("test_result", {})
    if isinstance(test, list):
        test = test[0] if len(test) > 0 else {}
    elif not isinstance(test, dict):
        test = {}
    
    st.markdown("---")
    st.subheader("📋 Autonomous Remediation & Verification Report")
    
    tab_overview, tab_diff, tab_test, tab_pr, tab_state, tab_graph = st.tabs([
        "📊 Code Health & Cost Audit",
        "🔄 Side-by-Side Git Diff",
        "🧪 Pytest Sandbox Terminal",
        "🐙 GitHub Pull Request",
        "🧩 LangGraph State Inspector",
        "🕸️ Project Graph Memory (Graphify)"
    ])
    
    with tab_overview:
        # Cost & Token Optimization Banner
        cost_info = res.get("cost_metrics", {})
        is_hit = res.get("cache_hit", False)
        
        st.markdown("#### 💰 API Cost & Token Economics (Enterprise Optimization)")
        cc1, cc2, cc3, cc4 = st.columns(4)
        with cc1:
            st.metric(
                label="Total Tokens Billed",
                value=f"{cost_info.get('total_tokens', 0):,}",
                delta="⚡ 0 tokens (Cached)" if is_hit else f"{cost_info.get('prompt_tokens', 0)} in / {cost_info.get('completion_tokens', 0)} out",
                delta_color="inverse" if is_hit else "normal"
            )
        with cc2:
            st.metric(
                label="Workflow Cost (USD)",
                value=f"${cost_info.get('cost_usd', 0.0):.5f}",
                delta="100% Free" if is_hit else "gpt-4o-mini tier",
                delta_color="normal"
            )
        with cc3:
            status_txt = "⚡ 100% CACHE HIT" if is_hit else "🔄 FRESH AUDIT"
            st.metric(
                label="Cache Acceleration",
                value=status_txt,
                delta="Bypassed LLMs" if is_hit else "Saved in Disk Cache",
                delta_color="normal" if is_hit else "off"
            )
        with cc4:
            st.metric(
                label="Cost Savings (USD)",
                value=f"${cost_info.get('savings_usd', 0.0):.5f}" if is_hit else "$0.00000",
                delta=f"+{cost_info.get('tokens_saved', 0):,} tokens saved" if is_hit else "Baseline run",
                delta_color="normal" if is_hit else "off"
            )

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            sev = sec.get("severity", "MEDIUM")
            badge_class = "badge-critical" if sev in ("CRITICAL", "HIGH") else "badge-safe"
            st.markdown(f"""
            <div class="metric-box">
                <h4>🛡️ Security Classification</h4>
                <p><strong>CWE ID:</strong> <code>{sec.get("cwe_id", "N/A")}</code></p>
                <p><strong>Severity:</strong> <span class="{badge_class}">{sev}</span></p>
                <p><strong>OWASP:</strong> {sec.get("owasp_category", "N/A")}</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-box">
                <h4>⚡ Algorithmic Optimization</h4>
                <p><strong>Time:</strong> <code>{comp.get("time_before", "N/A")}</code> ➔ <code>{comp.get("time_after", "N/A")}</code></p>
                <p><strong>Space:</strong> <code>{comp.get("space_before", "N/A")}</code> ➔ <code>{comp.get("space_after", "N/A")}</code></p>
                <p><strong>Improvement:</strong> {comp.get("improvement", "Optimized")}</p>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            p_status = "✅ PASSED" if test.get("passed") else "❌ FAILED"
            st.markdown(f"""
            <div class="metric-box">
                <h4>🧪 Test-Driven Verification</h4>
                <p><strong>Pytest Status:</strong> {p_status}</p>
                <p><strong>Self-Healing Retries:</strong> {res.get("retry_count", 0)} / {res.get("max_retries", 3)}</p>
                <p><strong>Sandbox Runtime:</strong> {test.get("duration_seconds", 0)}s</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("#### 🔍 Root Cause Analysis & Security Explanation")
        st.info(sec.get("explanation", "No security vulnerability detected."))
        st.markdown("#### ⚡ Algorithmic Complexity Breakdown")
        st.caption(comp.get("analysis", "No performance bottlenecks identified."))

    with tab_diff:
        st.markdown("#### 🔍 Side-by-Side Unified Diff")
        st.code(res.get("git_diff", "No diff available."), language="diff")
        
        st.markdown("#### 📄 Complete Patched Code (`solution.py`)")
        st.code(res.get("candidate_patch", ""), language="python")

    with tab_test:
        st.markdown("#### 🧪 Executed Pytest Test Suite (`test_solution.py`)")
        st.code(res.get("test_code", "# No tests"), language="python")
        
        st.markdown("#### 🖥️ Pytest Execution Terminal Output")
        stdout_txt = test.get("stdout", "")
        stderr_txt = test.get("stderr", "")
        term_output = stdout_txt if stdout_txt else stderr_txt
        st.code(term_output or "No output captured.", language="text")

    with tab_pr:
        st.markdown(f"### 📦 Staged PR: `{res.get('pr_title', 'Pull Request')}`")
        st.caption(f"**Target Branch:** `{res.get('git_branch', 'cognicode/fix')}` | **Commit:** `{res.get('commit_message', 'fix')}`")
        
        st.markdown("#### Pull Request Body Preview (Markdown)")
        st.markdown(res.get("pr_body", ""))
        
        if github_token and github_repo:
            if st.button("🚀 Push Branch & Open Real GitHub PR", type="primary"):
                from src.git_manager import create_github_pull_request
                with st.spinner("Pushing to GitHub via REST API..."):
                    pr_result = create_github_pull_request(
                        repo_full_name=github_repo,
                        branch_name=res.get("git_branch", "cognicode/fix"),
                        pr_title=res.get("pr_title", ""),
                        pr_body=res.get("pr_body", ""),
                        github_token=github_token
                    )
                if pr_result.get("success") and pr_result.get("pr_url"):
                    st.success(f"🎉 Live Pull Request Created: [View on GitHub]({pr_result['pr_url']})")
                else:
                    st.info(f"{pr_result.get('message', 'Local Git Mode active.')}")
        else:
            st.info("💡 **Local Git Mode Active**: Provide a GitHub Token & Repo in the sidebar if you wish to push this PR live to GitHub. Otherwise, use the generated diff above with `git apply`.")

    with tab_state:
        st.markdown("#### 🧠 Internal LangGraph `AgentState` Inspection")
        st.caption("Inspect the exact runtime state dictionary passed between nodes in the graph.")
        st.json(res)

    with tab_graph:
        st.markdown("### 🕸️ CogniCode Architectural Knowledge Graph (Graphify Memory)")
        st.caption("Deterministic AST Entity-Relationship Graph generated via `graphify_engine.py` (inspired by Graphify-Labs/graphify).")

        graph_html_path = os.path.join(os.path.dirname(__file__), "graphify-out", "graph.html")
        graph_json_path = os.path.join(os.path.dirname(__file__), "graphify-out", "graph.json")
        graph_report_path = os.path.join(os.path.dirname(__file__), "graphify-out", "GRAPH_REPORT.md")

        # Action row
        col_act1, col_act2, col_act3 = st.columns([2, 1, 1])
        with col_act1:
            if st.button("🔄 Re-Extract Knowledge Graph", key="btn_refresh_graph"):
                import subprocess
                subprocess.run([sys.executable, "graphify_engine.py"], capture_output=True)
                st.success("Knowledge Graph re-extracted successfully!")
                st.rerun()
        with col_act2:
            if os.path.exists(graph_json_path):
                with open(graph_json_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        label="📥 Download graph.json",
                        data=f.read(),
                        file_name="graph.json",
                        mime="application/json"
                    )
        with col_act3:
            if os.path.exists(graph_report_path):
                with open(graph_report_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        label="📄 Download GRAPH_REPORT.md",
                        data=f.read(),
                        file_name="GRAPH_REPORT.md",
                        mime="text/markdown"
                    )

        # Embedded Interactive Graph
        if os.path.exists(graph_html_path):
            with open(graph_html_path, "r", encoding="utf-8") as f:
                html_data = f.read()
            import streamlit.components.v1 as components
            components.html(html_data, height=720, scrolling=True)
        else:
            st.warning("graph.html not found. Run `python graphify_engine.py` to generate the interactive graph.")

        # Agent Bootstrap Prompt expander
        with st.expander("🤖 AI Agent Bootstrap & Context Injection Prompt (Copy for new AI sessions)", expanded=True):
            st.info("If your AI session context expires or tokens run out, paste this prompt into any new agent (Claude, ChatGPT, Antigravity) to resume development instantly:")
            if os.path.exists(graph_report_path):
                with open(graph_report_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
                st.code(report_content[:2000] + "\n\n... (See full GRAPH_REPORT.md for all 95 nodes & 617 edges)", language="markdown")
