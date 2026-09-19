import os
import sys
import time
import json
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
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .badge-critical { background-color: #ffebee; color: #c62828; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-high { background-color: #fff3e0; color: #ef6c00; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-safe { background-color: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .node-active {
        padding: 8px 12px;
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
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
        api_key_input = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            help="Your OpenAI API Key. Defaults to .env if set."
        )
        selected_model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    else:
        api_key_input = st.text_input(
            "Groq API Key",
            value=os.getenv("GROQ_API_KEY", ""),
            type="password",
            help="Your free Groq API Key"
        )
        selected_model = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"], index=0)
        
    max_retries = st.slider("Max Self-Healing Retries", min_value=1, max_value=5, value=3)
    
    st.markdown("---")
    st.subheader("🐙 GitHub Integration")
    github_token = st.text_input(
        "GitHub Token (Optional)",
        value=os.getenv("GITHUB_TOKEN", ""),
        type="password",
        help="Optional Personal Access Token to open live PRs"
    )
    github_repo = st.text_input(
        "GitHub Repo (e.g. user/repo)",
        value=os.getenv("GITHUB_REPOSITORY", ""),
        placeholder="Sapair-og/demo-repo"
    )
    
    st.markdown("---")
    st.markdown("""
    **Architecture Highlights:**
    - 🔍 **Symbolic AST:** Deterministic Python parser
    - 🧠 **Episodic Memory:** FAISS CWE/OWASP patterns
    - 🧪 **Sandbox:** Isolated Pytest runner
    - 🔄 **Cyclic Graph:** Self-healing reflection loop
    """)

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

# Execution Logic
if run_btn:
    if not api_key_input:
        st.error(f"Please provide an API key for {provider} in the sidebar or in your .env file.")
    elif not code_input.strip():
        st.warning("Please provide Python source code to analyze.")
    else:
        # Configure runtime environment
        if provider == "OpenAI":
            os.environ["OPENAI_API_KEY"] = api_key_input
        else:
            os.environ["GROQ_API_KEY"] = api_key_input
            
        from src.config import get_llm
        from src.nodes import set_runtime_llm
        from src.graph import cognicode_graph
        from src.state import AgentState
        
        try:
            runtime_llm = get_llm(
                provider=provider.lower(),
                model_name=selected_model,
                api_key=api_key_input,
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
            "node_history": []
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
    comp = res.get("complexity_report", {})
    test = res.get("test_result", {})
    
    st.markdown("---")
    st.subheader("📋 Autonomous Remediation & Verification Report")
    
    tab_overview, tab_diff, tab_test, tab_pr, tab_state = st.tabs([
        "📊 Code Health Audit",
        "🔄 Side-by-Side Git Diff",
        "🧪 Pytest Sandbox Terminal",
        "🐙 GitHub Pull Request",
        "🧩 LangGraph State Inspector"
    ])
    
    with tab_overview:
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
