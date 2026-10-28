import os
import sys
import time
import html
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

import streamlit as st

st.set_page_config(
    page_title="CogniCode",
    page_icon=":material/verified_user:",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT = os.path.dirname(os.path.abspath(__file__))
GRAPH_DIR = os.path.join(ROOT, "graphify-out")
REPO_URL = "https://github.com/Sapair-og/CogniCode"

# Theme colours, fonts and radius live in .streamlit/config.toml; this only adds the
# trace, KPI and status components Streamlit has no widget for.
st.markdown("""
<style>
:root {
    --ink: #15171C; --muted: #5D6472; --faint: #8A909C; --line: #E2E5EA;
    --surface: #FFFFFF; --canvas: #F5F6F8; --accent: #0B7A75; --accent-soft: #E3F2F1;
    --pass: #1E8E4E; --pass-soft: #E4F4EA; --fail: #C93A2B; --fail-soft: #FBE9E6;
    --warn: #A86400; --warn-soft: #FBF1DE;
    --mono: "IBM Plex Mono", ui-monospace, monospace;
}
.block-container { padding-top: 1.6rem; max-width: 1440px; }
.stTextArea textarea { font-family: var(--mono); font-size: 0.82rem; line-height: 1.6; }
header[data-testid="stHeader"] { background: transparent; }

.cc-brand { display: flex; align-items: center; gap: 10px; margin: 0 0 4px; }
.cc-brand svg { flex: none; }
.cc-brand b { font-size: 1.05rem; font-weight: 600; letter-spacing: -0.01em; }
.cc-brand span { display: block; color: var(--muted); font-size: 0.8rem; }

.cc-topbar { display: flex; align-items: center; justify-content: space-between; gap: 16px;
    padding-bottom: 14px; margin-bottom: 18px; border-bottom: 1px solid var(--line); flex-wrap: wrap; }
.cc-crumbs { color: var(--muted); font-size: 0.86rem; }
.cc-crumbs b { color: var(--ink); font-weight: 600; }
.cc-crumbs i { font-style: normal; color: var(--faint); padding: 0 6px; }
.cc-title { font-size: 1.45rem; font-weight: 600; letter-spacing: -0.015em; margin: 2px 0 0; }

.cc-pill { display: inline-flex; align-items: center; gap: 6px; padding: 2px 9px; border-radius: 999px;
    font-size: 0.78rem; font-weight: 500; border: 1px solid transparent; white-space: nowrap; }
.cc-pill::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.cc-pill.pass { color: var(--pass); background: var(--pass-soft); }
.cc-pill.fail { color: var(--fail); background: var(--fail-soft); }
.cc-pill.warn { color: var(--warn); background: var(--warn-soft); }
.cc-pill.idle { color: var(--muted); background: var(--canvas); border-color: var(--line); }
.cc-pill.run  { color: var(--accent); background: var(--accent-soft); }
.cc-pill.run::before { animation: cc-pulse 1.1s ease-in-out infinite; }
@keyframes cc-pulse { 50% { opacity: 0.25; } }

.cc-panel-head { display: flex; align-items: baseline; justify-content: space-between; margin: 0 0 8px; }
.cc-panel-head h3 { font-size: 0.95rem; font-weight: 600; margin: 0; padding: 0; }
.cc-panel-head span { color: var(--muted); font-size: 0.8rem; }

/* Trace waterfall */
.cc-trace { border: 1px solid var(--line); border-radius: 8px; background: var(--surface); overflow: hidden; }
.cc-trace-head, .cc-span { display: grid; grid-template-columns: minmax(150px, 1.25fr) 74px minmax(120px, 2fr) 64px;
    align-items: center; gap: 12px; padding: 0 14px; }
.cc-trace-head { height: 32px; font-size: 0.75rem; color: var(--faint); border-bottom: 1px solid var(--line); background: var(--canvas); }
.cc-span { min-height: 44px; border-bottom: 1px solid var(--line); font-size: 0.86rem; }
.cc-span:last-child { border-bottom: 0; }
.cc-span .name { display: flex; align-items: center; gap: 8px; min-width: 0; }
.cc-span .name b { font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cc-span .name small { display: block; color: var(--faint); font-size: 0.74rem; font-weight: 400; }
.cc-dot { width: 8px; height: 8px; border-radius: 50%; flex: none; background: var(--line); }
.cc-dot.ok { background: var(--accent); } .cc-dot.pass { background: var(--pass); }
.cc-dot.fail { background: var(--fail); } .cc-dot.warn { background: var(--warn); }
.cc-dot.live { background: var(--accent); animation: cc-pulse 1.1s ease-in-out infinite; }
.cc-kind { font-family: var(--mono); font-size: 0.72rem; color: var(--muted); }
.cc-kind.llm { color: #6A3FB5; } .cc-kind.tool { color: #1F5FA8; }
.cc-track { position: relative; height: 8px; background: var(--canvas); border-radius: 4px; }
.cc-bar { position: absolute; top: 0; height: 8px; border-radius: 4px; background: var(--accent); min-width: 3px; }
.cc-bar.llm { background: #8A63D2; } .cc-bar.tool { background: #3B7DD8; }
.cc-bar.fail { background: var(--fail); } .cc-bar.pending { background: transparent; }
.cc-dur { font-family: var(--mono); font-size: 0.78rem; text-align: right; color: var(--ink); }
.cc-span.pending { color: var(--faint); }
.cc-span.pending .cc-dur { color: var(--faint); }
.cc-trace-note { padding: 12px 14px; color: var(--muted); font-size: 0.84rem; border-top: 1px solid var(--line); background: var(--canvas); }

/* KPI strip */
.cc-kpis { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); border: 1px solid var(--line);
    border-radius: 8px; background: var(--surface); margin: 22px 0 6px; }
.cc-kpi { padding: 14px 16px; border-left: 1px solid var(--line); min-width: 0; }
.cc-kpi:first-child { border-left: 0; }
.cc-kpi label { display: block; color: var(--muted); font-size: 0.78rem; margin-bottom: 4px; }
.cc-kpi div { font-size: 1.25rem; font-weight: 600; letter-spacing: -0.01em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cc-kpi small { display: block; color: var(--faint); font-size: 0.76rem; margin-top: 2px; }
.cc-kpi .mono { font-family: var(--mono); font-weight: 500; }

/* Findings */
.cc-card { border: 1px solid var(--line); border-radius: 8px; background: var(--surface); padding: 16px 18px; height: 100%; }
.cc-card h4 { font-size: 0.92rem; font-weight: 600; margin: 0 0 12px; padding: 0; display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.cc-card p { color: var(--ink); font-size: 0.88rem; line-height: 1.55; margin: 12px 0 0; }
.cc-rows { display: grid; grid-template-columns: max-content 1fr; gap: 6px 16px; font-size: 0.86rem; }
.cc-card dl.cc-rows { margin: 0; padding: 0; }
.cc-card .cc-rows dt { color: var(--muted); font-size: 0.86rem; font-weight: 400; margin: 0; padding: 0; line-height: 1.5; }
.cc-card .cc-rows dd { margin: 0; padding: 0; font-family: var(--mono); font-size: 0.82rem; line-height: 1.5; }
.cc-bigo { display: flex; align-items: baseline; gap: 10px; font-family: var(--mono); font-size: 1.15rem; margin-bottom: 4px; }
.cc-bigo s { color: var(--fail); text-decoration-thickness: 1px; }
.cc-bigo b { color: var(--pass); font-weight: 500; }

.cc-empty { border: 1px dashed var(--line); border-radius: 8px; padding: 28px; color: var(--muted); text-align: center; font-size: 0.9rem; }
.cc-side-label { color: var(--muted); font-size: 0.78rem; font-weight: 500; margin: 14px 0 2px; }
.cc-gw { display: flex; align-items: center; gap: 8px; font-size: 0.82rem; color: var(--muted); }
.cc-gw b { color: var(--ink); font-weight: 500; }

@media (max-width: 900px) {
    .cc-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .cc-kpi:nth-child(odd) { border-left: 0; }
    .cc-kpi:nth-child(n+3) { border-top: 1px solid var(--line); }
    .cc-trace-head, .cc-span { grid-template-columns: minmax(120px, 1fr) 64px 56px; }
    .cc-trace-head > :nth-child(3), .cc-span > .cc-track { display: none; }
}
@media (prefers-reduced-motion: reduce) {
    .cc-pill.run::before, .cc-dot.live { animation: none; }
}
</style>
""", unsafe_allow_html=True)

# Graph node -> (label, what it does, kind). Kind drives the trace colour, like a
# Langfuse span vs generation.
STEPS = {
    "retrieve_memory": ("Memory lookup", "FAISS pattern bank + triage", "retrieval"),
    "symbolic_ast": ("AST analysis", "ast parser, cache check", "tool"),
    "security_audit": ("Security audit", "CWE / OWASP classification", "llm"),
    "complexity_profiler": ("Complexity profile", "Big-O before and after", "llm"),
    "patch_synthesizer": ("Patch and tests", "writes fix + pytest suite", "llm"),
    "sandbox_verifier": ("Sandbox run", "pytest with timeout", "tool"),
    "self_healing_reflection": ("Self-repair", "reads failure, rewrites patch", "llm"),
    "git_pr": ("Pull request draft", "diff, branch, PR body", "tool"),
}
HAPPY_PATH = ["retrieve_memory", "symbolic_ast", "security_audit", "complexity_profiler",
              "patch_synthesizer", "sandbox_verifier", "git_pr"]


def esc(value) -> str:
    return html.escape(str(value))


def as_dict(value) -> dict:
    """LLM nodes occasionally return a one-item list instead of a dict."""
    if isinstance(value, list):
        value = value[0] if value else {}
    return value if isinstance(value, dict) else {}


def pill(text: str, tone: str) -> str:
    return f'<span class="cc-pill {tone}">{esc(text)}</span>'


def fmt_ms(seconds: float) -> str:
    return f"{seconds * 1000:.0f} ms" if seconds < 1 else f"{seconds:.2f} s"


def span_tone(span: dict) -> str:
    if span.get("error"):
        return "fail"
    if span["node"] == "sandbox_verifier":
        return "pass" if span.get("passed") else "fail"
    if span["node"] == "symbolic_ast" and span.get("cache_hit"):
        return "pass"
    return "ok"


def render_trace(spans: list, running: bool = False, note: str = "") -> str:
    total = max(sum(s["dur"] for s in spans), 1e-6)
    rows = []
    for s in spans:
        label, desc, kind = STEPS.get(s["node"], (s["node"], "", "tool"))
        tone = span_tone(s)
        if s["node"] == "sandbox_verifier":
            desc = "tests passed" if s.get("passed") else "tests failed"
        if s["node"] == "symbolic_ast" and s.get("cache_hit"):
            desc = "cache hit, LLM steps skipped"
        left = s["start"] / total * 100
        width = s["dur"] / total * 100
        bar_cls = "fail" if tone == "fail" else kind
        rows.append(
            f'<div class="cc-span"><div class="name"><span class="cc-dot {tone}"></span>'
            f'<div><b>{esc(label)}</b><small>{esc(desc)}</small></div></div>'
            f'<span class="cc-kind {kind}">{kind}</span>'
            f'<div class="cc-track"><div class="cc-bar {bar_cls}" style="left:{left:.2f}%;width:{width:.2f}%"></div></div>'
            f'<span class="cc-dur">{fmt_ms(s["dur"])}</span></div>'
        )
    if running:
        rows.append(
            '<div class="cc-span pending"><div class="name"><span class="cc-dot live"></span>'
            '<div><b>Running next step</b><small>waiting for the agent</small></div></div>'
            '<span class="cc-kind"></span><div class="cc-track"></div><span class="cc-dur">…</span></div>'
        )
    if not spans and not running:
        for node in HAPPY_PATH:
            label, desc, kind = STEPS[node]
            rows.append(
                f'<div class="cc-span pending"><div class="name"><span class="cc-dot"></span>'
                f'<div><b>{esc(label)}</b><small>{esc(desc)}</small></div></div>'
                f'<span class="cc-kind {kind}">{kind}</span><div class="cc-track"></div>'
                f'<span class="cc-dur">–</span></div>'
            )
    note_html = f'<div class="cc-trace-note">{note}</div>' if note else ""
    return (
        '<div class="cc-trace"><div class="cc-trace-head"><span>Step</span><span>Type</span>'
        '<span>Timeline</span><span style="text-align:right">Duration</span></div>'
        + "".join(rows) + "</div>" + note_html
    )


# Load Presets
PRESETS = {
    "SQL injection (CWE-89)": (
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
    "Exponential recursion, O(2^N) (CWE-400)": (
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
    "O(N^2) two-sum plus SQL injection": (
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
    "Null dereference (CWE-476)": (
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
    "Your own code": "def example():\n    pass\n",
}

# ---------------------------------------------------------------- sidebar
BRAND_MARK = (
    '<svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true">'
    '<rect width="26" height="26" rx="6" fill="#0B7A75"/>'
    '<path d="M7.5 13.5l3.6 3.6 7.4-8.2" fill="none" stroke="#fff" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

with st.sidebar:
    st.markdown(
        f'<div class="cc-brand">{BRAND_MARK}<div><b>CogniCode</b>'
        '<span>Finds, fixes and tests Python bugs</span></div></div>',
        unsafe_allow_html=True,
    )
    page = st.segmented_control(
        "Page", ["Playground", "Knowledge graph"], default="Playground",
        label_visibility="collapsed", width="stretch",
    ) or "Playground"

    st.markdown('<div class="cc-side-label">Model</div>', unsafe_allow_html=True)
    provider = st.selectbox(
        "Provider", ["OpenAI", "Groq"], index=0,
        help="Groq has a free tier: console.groq.com/keys",
    )
    env_key_name = "OPENAI_API_KEY" if provider == "OpenAI" else "GROQ_API_KEY"
    env_key = os.getenv(env_key_name, "").strip()
    # Never echo a server-side key into the page: password inputs still send their value
    # to the browser. The server key is only used as a fallback when this field is empty.
    api_key_input = st.text_input(
        f"{provider} API key", type="password",
        placeholder="Using the server key" if env_key else "Paste your key",
        help="Used for this session only and never stored.",
    )
    if provider == "OpenAI":
        selected_model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    else:
        selected_model = st.selectbox("Model", ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"], index=0)

    max_retries = st.slider("Self-repair attempts", min_value=1, max_value=5, value=3,
                            help="How many times the agent may rewrite a patch whose tests fail.")

    with st.expander("Integrations"):
        env_typesafe_key = os.getenv("TYPESAFE_API_KEY", "") or os.getenv("JEV_API_KEY", "")
        typesafe_api_key_input = st.text_input(
            "TypeSafe Jev key", type="password",
            placeholder="Using the server key" if env_typesafe_key else "Optional",
            help="Fast pre-LLM risk triage. Without a key a local evaluator runs instead.",
        )
        env_gh_token = os.getenv("GITHUB_TOKEN", "").strip()
        github_token_input = st.text_input(
            "GitHub token", type="password",
            placeholder="Using the server token" if env_gh_token else "Optional, to open real PRs",
        )
        github_token = (github_token_input or "").strip() or env_gh_token
        github_repo = st.text_input("GitHub repo", value=os.getenv("GITHUB_REPOSITORY", ""),
                                    placeholder="owner/repo")

    from src.gateway import llm_gateway
    gw_health = llm_gateway.get_gateway_health()
    has_key = bool((api_key_input or "").strip() or env_key)
    gw_tone = "pass" if has_key else "warn"
    gw_text = "Ready" if has_key else "Needs a key"
    st.markdown('<div class="cc-side-label">Gateway</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="cc-gw">{pill(gw_text, gw_tone)}<span>Fallback: <b>{esc(gw_health["fallback_route"])}</b></span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="cc-side-label"><a href="{REPO_URL}" target="_blank">Source on GitHub</a></div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------- knowledge graph page
def knowledge_graph_page():
    graph_html_path = os.path.join(GRAPH_DIR, "graph.html")
    graph_json_path = os.path.join(GRAPH_DIR, "graph.json")
    graph_report_path = os.path.join(GRAPH_DIR, "GRAPH_REPORT.md")

    st.markdown(
        '<div class="cc-topbar"><div><div class="cc-crumbs">CogniCode<i>/</i><b>Knowledge graph</b></div>'
        '<div class="cc-title">How this repository fits together</div></div></div>',
        unsafe_allow_html=True,
    )
    st.caption("Modules, classes and functions extracted from the AST by graphify_engine.py. "
               "A compact summary of it is added to agent prompts.")

    a1, a2, a3, _ = st.columns([1.2, 1.2, 1.4, 3])
    with a1:
        if st.button("Rebuild graph", icon=":material/refresh:", width="stretch"):
            import subprocess
            with st.spinner("Rebuilding from the AST..."):
                subprocess.run([sys.executable, "graphify_engine.py"], capture_output=True, cwd=ROOT)
            st.toast("Graph rebuilt")
            st.rerun()
    with a2:
        if os.path.exists(graph_json_path):
            with open(graph_json_path, "r", encoding="utf-8") as f:
                st.download_button("graph.json", f.read(), file_name="graph.json",
                                   mime="application/json", icon=":material/download:", width="stretch")
    with a3:
        if os.path.exists(graph_report_path):
            with open(graph_report_path, "r", encoding="utf-8") as f:
                st.download_button("GRAPH_REPORT.md", f.read(), file_name="GRAPH_REPORT.md",
                                   mime="text/markdown", icon=":material/download:", width="stretch")

    if os.path.exists(graph_html_path):
        import streamlit.components.v1 as components
        with open(graph_html_path, "r", encoding="utf-8") as f:
            components.html(f.read(), height=720, scrolling=True)
    else:
        st.markdown('<div class="cc-empty">No graph yet. Press <b>Rebuild graph</b> to generate it.</div>',
                    unsafe_allow_html=True)

    if os.path.exists(graph_report_path):
        with st.expander("Summary given to the agents"):
            with open(graph_report_path, "r", encoding="utf-8") as f:
                st.code(f.read()[:2000], language="markdown")


if page == "Knowledge graph":
    knowledge_graph_page()
    st.stop()


# ---------------------------------------------------------------- playground page
result = st.session_state.get("cognicode_result")

top_left, top_right = st.columns([3, 1], vertical_alignment="bottom")
with top_left:
    title_ph = st.empty()
with top_right:
    status_ph = st.empty()


def render_topbar(status: str, tone: str):
    run_id = st.session_state.get("cognicode_run_id")
    crumb = f"Run {esc(run_id)}" if run_id else "New run"
    title_ph.markdown(
        f'<div class="cc-crumbs">CogniCode<i>/</i>Playground<i>/</i><b>{crumb}</b></div>'
        '<div class="cc-title">Find, fix and verify a Python function</div>',
        unsafe_allow_html=True,
    )
    status_ph.markdown(f'<div style="text-align:right">{pill(status, tone)}</div>', unsafe_allow_html=True)


if result:
    verified = result.get("status") == "verified"
    render_topbar("Verified" if verified else "Needs review", "pass" if verified else "warn")
else:
    render_topbar("Idle", "idle")
st.markdown('<div class="cc-topbar"></div>', unsafe_allow_html=True)

col_left, col_right = st.columns([5, 6], gap="large")

with col_left:
    st.markdown('<div class="cc-panel-head"><h3>Source</h3><span>solution.py</span></div>', unsafe_allow_html=True)
    preset_choice = st.selectbox("Sample", list(PRESETS.keys()), label_visibility="collapsed")
    code_input = st.text_area(
        "Python source", value=PRESETS[preset_choice], height=360,
        label_visibility="collapsed", key=f"code_{preset_choice}",
        help="Paste one Python file. Functions are analysed, patched and tested on their own.",
    )
    run_btn = st.button("Run agents", type="primary", icon=":material/play_arrow:", width="stretch")
    if not has_key:
        st.caption(f"Add {'an' if provider == 'OpenAI' else 'a'} {provider} API key in the sidebar to run. Groq keys are free.")

with col_right:
    head_ph = st.empty()
    trace_ph = st.empty()


def show_trace_head(meta: str):
    head_ph.markdown(f'<div class="cc-panel-head"><h3>Trace</h3><span>{meta}</span></div>', unsafe_allow_html=True)


if result:
    spans = st.session_state.get("cognicode_spans", [])
    total = sum(s["dur"] for s in spans)
    show_trace_head(f"{len(spans)} steps, {fmt_ms(total)}")
    trace_ph.markdown(render_trace(spans), unsafe_allow_html=True)
else:
    show_trace_head("not run yet")
    trace_ph.markdown(
        render_trace([], note="Pick a sample and press <b>Run agents</b>. Each step shows up here as it finishes, "
                              "with its duration. Failed tests loop through self-repair before the PR draft."),
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------- run
if run_btn:
    effective_key = (api_key_input or "").strip() or env_key
    if not effective_key:
        st.error(f"No {provider} API key. Paste one in the sidebar under Model, then run again.")
        st.stop()
    if not code_input.strip():
        st.error("The source is empty. Paste a Python function or pick a sample.")
        st.stop()

    os.environ[env_key_name] = effective_key
    if typesafe_api_key_input and typesafe_api_key_input.strip():
        os.environ["TYPESAFE_API_KEY"] = typesafe_api_key_input.strip()
        from src.jev_client import jev_client
        jev_client.api_key = typesafe_api_key_input.strip()

    from src.config import get_llm
    from src.nodes import set_runtime_llm
    from src.graph import cognicode_graph
    from src.state import AgentState

    try:
        runtime_llm = get_llm(provider=provider.lower(), model_name=selected_model,
                              api_key=effective_key, temperature=0.1)
        set_runtime_llm(llm_gateway.with_runtime_failover(runtime_llm, provider.lower(), 0.1))
    except Exception as e:
        st.error(f"Could not start the {provider} model: {e}")
        st.stop()

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
        "cost_metrics": {},
        "jev_triage": {}
    }

    st.session_state["cognicode_run_id"] = format(int(time.time() * 1000) % 0xFFFFFF, "06x")
    render_topbar("Running", "run")
    state = dict(initial_state)
    spans = []
    t0 = last = time.perf_counter()
    trace_ph.markdown(render_trace(spans, running=True), unsafe_allow_html=True)

    # Stream node-by-node so the trace fills in live. Nodes return partial state, and the
    # graph has no reducers, so merging updates in order rebuilds the final state.
    try:
        for chunk in cognicode_graph.stream(initial_state, stream_mode="updates"):
            for node, update in chunk.items():
                now = time.perf_counter()
                update = update or {}
                state.update(update)
                span = {"node": node, "start": last - t0, "dur": now - last}
                if node == "sandbox_verifier":
                    span["passed"] = bool(as_dict(update.get("test_result")).get("passed"))
                if node == "symbolic_ast":
                    span["cache_hit"] = bool(update.get("cache_hit"))
                spans.append(span)
                last = now
            show_trace_head(f"{len(spans)} steps, {fmt_ms(last - t0)}")
            trace_ph.markdown(render_trace(spans, running=True), unsafe_allow_html=True)
    except Exception as e:
        spans.append({"node": "error", "start": last - t0, "dur": time.perf_counter() - last, "error": True})
        trace_ph.markdown(render_trace(spans), unsafe_allow_html=True)
        render_topbar("Failed", "fail")
        st.error(f"The run stopped: {e}")
        st.stop()

    st.session_state["cognicode_result"] = state
    st.session_state["cognicode_spans"] = spans
    st.rerun()

# ---------------------------------------------------------------- results
if not result:
    st.stop()

res = result
sec = as_dict(res.get("security_report"))
comp = as_dict(res.get("complexity_report"))
test = as_dict(res.get("test_result"))
cost_info = as_dict(res.get("cost_metrics"))
jev = as_dict(res.get("jev_triage"))
is_hit = res.get("cache_hit", False)
verified = res.get("status") == "verified"
spans = st.session_state.get("cognicode_spans", [])
retries = res.get("retry_count", 0)

kpis = [
    ("Outcome", "Verified" if verified else "Needs review",
     "tests pass on the patch" if verified else "tests still fail, flagged in PR"),
    ("Latency", f'<span class="mono">{fmt_ms(sum(s["dur"] for s in spans))}</span>', f"{len(spans)} steps"),
    ("Tokens", f'<span class="mono">{cost_info.get("total_tokens", 0):,}</span>',
     "served from cache" if is_hit else f'{cost_info.get("prompt_tokens", 0):,} in, {cost_info.get("completion_tokens", 0):,} out'),
    ("Cost", f'<span class="mono">${cost_info.get("cost_usd", 0.0):.4f}</span>',
     f'saved ${cost_info.get("savings_usd", 0.0):.4f}' if is_hit else "this run"),
    ("Self-repair", f'<span class="mono">{retries} / {res.get("max_retries", 3)}</span>',
     "first patch passed" if retries == 0 and verified else "patch rewrites"),
    ("Sandbox", f'<span class="mono">{esc(test.get("duration_seconds", 0))} s</span>',
     "pytest " + ("passed" if test.get("passed") else "failed")),
]
st.markdown(
    '<div class="cc-kpis">' + "".join(
        f'<div class="cc-kpi"><label>{esc(k)}</label><div>{v}</div><small>{esc(s)}</small></div>' for k, v, s in kpis
    ) + "</div>",
    unsafe_allow_html=True,
)

tab_overview, tab_diff, tab_test, tab_pr, tab_state = st.tabs(
    ["Findings", "Patch", "Tests", "Pull request", "State"]
)

with tab_overview:
    c1, c2 = st.columns(2, gap="medium")
    sev = str(sec.get("severity", "MEDIUM")).upper()
    sev_tone = "fail" if sev in ("CRITICAL", "HIGH") else ("warn" if sev == "MEDIUM" else "pass")
    with c1:
        st.markdown(
            f'<div class="cc-card"><h4>Security {pill(sev.title(), sev_tone)}</h4>'
            f'<dl class="cc-rows"><dt>Weakness</dt><dd>{esc(sec.get("cwe_id", "None found"))}</dd>'
            f'<dt>OWASP</dt><dd>{esc(sec.get("owasp_category", "n/a"))}</dd></dl>'
            f'<p>{esc(sec.get("explanation", "No security issue found."))}</p></div>',
            unsafe_allow_html=True,
        )
    t_before, t_after = comp.get("time_before", "n/a"), comp.get("time_after", "n/a")
    if t_before != t_after:
        bigo = f'<div class="cc-bigo"><s>{esc(t_before)}</s><span>to</span><b>{esc(t_after)}</b></div>'
    else:
        bigo = f'<div class="cc-bigo"><span>{esc(t_after)}</span></div>'
    with c2:
        st.markdown(
            f'<div class="cc-card"><h4>Performance</h4>'
            f'{bigo}'
            f'<dl class="cc-rows"><dt>Space</dt><dd>{esc(comp.get("space_before", "n/a"))} to {esc(comp.get("space_after", "n/a"))}</dd></dl>'
            f'<p>{esc(comp.get("analysis") or comp.get("improvement") or "No bottleneck found.")}</p></div>',
            unsafe_allow_html=True,
        )
    if jev:
        r_score = jev.get("risk_score", 0)
        r_tone = "fail" if r_score >= 6 else ("warn" if r_score >= 4 else "pass")
        source = "TypeSafe Jev API" if jev.get("live_api") else "local evaluator"
        st.markdown(
            f'<div class="cc-card" style="margin-top:14px"><h4>Pre-LLM triage {pill(f"Risk {r_score}/10", r_tone)}</h4>'
            f'<dl class="cc-rows"><dt>Verdict</dt><dd>{"vulnerable" if jev.get("has_vulnerability") else "clean"} '
            f'({int(jev.get("vuln_confidence", 0.9) * 100)}% confidence)</dd>'
            f'<dt>Class</dt><dd>{esc(jev.get("cwe_choice", "n/a"))}, {esc(jev.get("complexity_choice", "n/a"))}</dd>'
            f'<dt>Latency</dt><dd>{esc(jev.get("latency_ms", 0))} ms via {source}</dd></dl></div>',
            unsafe_allow_html=True,
        )

with tab_diff:
    st.markdown('<div class="cc-panel-head"><h3>Unified diff</h3><span>apply with git apply</span></div>', unsafe_allow_html=True)
    st.code(res.get("git_diff") or "No changes.", language="diff")
    st.markdown('<div class="cc-panel-head"><h3>Patched file</h3><span>solution.py</span></div>', unsafe_allow_html=True)
    st.code(res.get("candidate_patch", ""), language="python")

with tab_test:
    st.markdown(
        f'<div class="cc-panel-head"><h3>Generated tests</h3>{pill("Passed" if test.get("passed") else "Failed", "pass" if test.get("passed") else "fail")}</div>',
        unsafe_allow_html=True,
    )
    st.code(res.get("test_code") or "# No tests generated", language="python")
    st.markdown('<div class="cc-panel-head"><h3>pytest output</h3></div>', unsafe_allow_html=True)
    st.code(test.get("stdout") or test.get("stderr") or "No output captured.", language="text")

with tab_pr:
    st.markdown(
        f'<div class="cc-panel-head"><h3>{esc(res.get("pr_title") or "Pull request")}</h3>'
        f'<span>{esc(res.get("git_branch") or "cognicode/fix")}</span></div>',
        unsafe_allow_html=True,
    )
    st.caption(f'Commit message: {res.get("commit_message") or "fix"}')
    with st.container(border=True):
        st.markdown(res.get("pr_body", ""))
    if github_token and github_repo:
        if st.button("Open pull request on GitHub", type="primary", icon=":material/merge:"):
            from src.git_manager import create_github_pull_request
            with st.spinner("Pushing the branch and opening the PR..."):
                pr_result = create_github_pull_request(
                    repo_full_name=github_repo,
                    branch_name=res.get("git_branch", "cognicode/fix"),
                    pr_title=res.get("pr_title", ""),
                    pr_body=res.get("pr_body", ""),
                    github_token=github_token
                )
            if pr_result.get("success") and pr_result.get("pr_url"):
                st.success(f"Pull request opened: [view on GitHub]({pr_result['pr_url']})")
            else:
                st.error(pr_result.get("message", "GitHub did not accept the pull request."))
    else:
        st.caption("To open this as a real PR, add a GitHub token and repo under Integrations in the sidebar. "
                   "Otherwise apply the diff from the Patch tab with git apply.")

with tab_state:
    st.caption("The AgentState dictionary passed between graph nodes, as it was after the last step.")
    st.json(res, expanded=1)
