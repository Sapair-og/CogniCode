"""
Graphify Engine for CogniCode
=============================
Inspired by Graphify (Graphify-Labs/graphify).
Transforms the entire CogniCode codebase into a queryable, visual knowledge graph
with machine-readable graph.json, interactive graph.html, and GRAPH_REPORT.md.

Produces an AI Agent Bootstrap Memory Layer so any future AI agent can ingest
this single artifact and immediately understand and continue development
without reading raw files or exhausting context windows.
"""

import os
import sys
import ast
import json
from typing import Dict, List, Any, Set
from collections import defaultdict

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "graphify-out")

NODE_CATEGORIES = {
    "module": {"color": "#4a90e2", "shape": "box", "size": 25},
    "class": {"color": "#9b59b6", "shape": "diamond", "size": 25},
    "function": {"color": "#2ecc71", "shape": "dot", "size": 18},
    "langgraph_node": {"color": "#e67e22", "shape": "star", "size": 28},
    "state_key": {"color": "#1abc9c", "shape": "ellipse", "size": 16},
    "prompt": {"color": "#e74c3c", "shape": "triangle", "size": 20},
    "ui": {"color": "#f39c12", "shape": "box", "size": 22},
    "test_sample": {"color": "#95a5a6", "shape": "dot", "size": 14}
}

class CodebaseGraphExtractor:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.in_degree = defaultdict(int)
        self.out_degree = defaultdict(int)

    def add_node(self, node_id: str, label: str, category: str, file_path: str, docstring: str = "", metadata: Dict[str, Any] = None):
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "label": label,
                "category": category,
                "file": file_path,
                "docstring": (docstring or "").strip(),
                "metadata": metadata or {},
                "in_degree": 0,
                "out_degree": 0
            }

    def add_edge(self, source: str, target: str, relationship: str, metadata: Dict[str, Any] = None):
        if not source or not target or source == target:
            return
        edge = {
            "source": source,
            "target": target,
            "relationship": relationship,
            "metadata": metadata or {}
        }
        self.edges.append(edge)
        self.out_degree[source] += 1
        self.in_degree[target] += 1

    def scan_project(self):
        target_dirs = ["src", "samples"]
        target_files = ["app.py", "run_demo_test.py"]

        # Parse files in target directories
        for d in target_dirs:
            dir_path = os.path.join(self.root_dir, d)
            if not os.path.exists(dir_path):
                continue
            for root, _, files in os.walk(dir_path):
                for f in files:
                    if f.endswith(".py"):
                        full_path = os.path.join(root, f)
                        rel_path = os.path.relpath(full_path, self.root_dir).replace("\\", "/")
                        self._analyze_file(full_path, rel_path)

        # Parse root script files
        for f in target_files:
            full_path = os.path.join(self.root_dir, f)
            if os.path.exists(full_path):
                self._analyze_file(full_path, f)

        # Add explicit LangGraph State Keys
        self._add_state_schema_nodes()

        # Add explicit LangGraph Transitions
        self._add_langgraph_transitions()

        # Update degree counts on nodes
        for node_id, node_data in self.nodes.items():
            node_data["in_degree"] = self.in_degree[node_id]
            node_data["out_degree"] = self.out_degree[node_id]
            node_data["total_degree"] = self.in_degree[node_id] + self.out_degree[node_id]

    def _analyze_file(self, full_path: str, rel_path: str):
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=rel_path)
        except Exception as e:
            print(f"Skipping {rel_path} due to parse error: {e}")
            return

        module_id = f"module::{rel_path}"
        mod_category = "ui" if "app.py" in rel_path else ("test_sample" if "samples" in rel_path else "module")
        docstring = ast.get_docstring(tree) or ""
        self.add_node(module_id, rel_path, mod_category, rel_path, docstring=docstring)

        # Walk AST to find classes, functions, and imports
        for node in tree.body:
            # Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imp_id = f"module::{alias.name}.py"
                    self.add_edge(module_id, imp_id, "IMPORTS")
            elif isinstance(node, ast.ImportFrom):
                mod_name = node.module or ""
                target_mod_id = f"module::{mod_name.replace('.', '/')}.py"
                self.add_edge(module_id, target_mod_id, "IMPORTS")

            # Classes
            elif isinstance(node, ast.ClassDef):
                class_id = f"class::{rel_path}::{node.name}"
                class_doc = ast.get_docstring(node) or ""
                self.add_node(class_id, node.name, "class", rel_path, docstring=class_doc)
                self.add_edge(module_id, class_id, "CONTAINS")

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        meth_id = f"func::{rel_path}::{node.name}.{item.name}"
                        meth_doc = ast.get_docstring(item) or ""
                        self.add_node(meth_id, f"{node.name}.{item.name}()", "function", rel_path, docstring=meth_doc)
                        self.add_edge(class_id, meth_id, "CONTAINS")
                        self._analyze_function_body(item, meth_id, rel_path)

            # Top-level Functions
            elif isinstance(node, ast.FunctionDef):
                is_graph_node = node.name.endswith("_node")
                cat = "langgraph_node" if is_graph_node else "function"
                func_id = f"node::{node.name}" if is_graph_node else f"func::{rel_path}::{node.name}"
                func_doc = ast.get_docstring(node) or ""
                self.add_node(func_id, f"{node.name}()", cat, rel_path, docstring=func_doc)
                self.add_edge(module_id, func_id, "CONTAINS")
                self._analyze_function_body(node, func_id, rel_path)

            # Prompts and Models in chains.py
            elif isinstance(node, ast.Assign) and "chains.py" in rel_path:
                for target in node.targets:
                    if isinstance(target, ast.Name) and "PROMPT" in target.id:
                        p_id = f"prompt::{target.id}"
                        self.add_node(p_id, target.id, "prompt", rel_path, docstring="Prompt Template")
                        self.add_edge(module_id, p_id, "CONTAINS")

    def _analyze_function_body(self, func_node: ast.FunctionDef, caller_id: str, rel_path: str):
        for sub in ast.walk(func_node):
            # Function Calls
            if isinstance(sub, ast.Call):
                if isinstance(sub.func, ast.Name):
                    target_func = sub.func.id
                    self.add_edge(caller_id, f"func::{target_func}", "CALLS")
                elif isinstance(sub.func, ast.Attribute):
                    target_attr = sub.func.attr
                    self.add_edge(caller_id, f"func::{target_attr}", "CALLS")

            # State Reads: state["..."] or state.get("...")
            if isinstance(sub, ast.Subscript):
                if isinstance(sub.value, ast.Name) and sub.value.id == "state":
                    if isinstance(sub.slice, ast.Constant) and isinstance(sub.slice.value, str):
                        key_id = f"state_key::{sub.slice.value}"
                        self.add_edge(caller_id, key_id, "READS_STATE")
            elif isinstance(sub, ast.Call):
                if isinstance(sub.func, ast.Attribute) and sub.func.attr == "get":
                    if isinstance(sub.func.value, ast.Name) and sub.func.value.id == "state":
                        if sub.args and isinstance(sub.args[0], ast.Constant) and isinstance(sub.args[0].value, str):
                            key_id = f"state_key::{sub.args[0].value}"
                            self.add_edge(caller_id, key_id, "READS_STATE")

            # State Writes: return { "key": ... }
            if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Dict):
                for k in sub.value.keys:
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        key_id = f"state_key::{k.value}"
                        self.add_edge(caller_id, key_id, "WRITES_STATE")

    def _add_state_schema_nodes(self):
        state_fields = [
            ("source_code", "Original code under inspection"),
            ("filename", "Target filename e.g. solution.py"),
            ("language", "Language (python)"),
            ("ast_analysis", "Deterministic AST metrics & dangerous call detection"),
            ("retrieved_patterns", "Few-shot CWE patterns from FAISS vector bank"),
            ("security_report", "CWE vulnerability classification & severity"),
            ("complexity_report", "Big-O runtime & memory profiling"),
            ("candidate_patch", "Refactored/remediated code solution"),
            ("test_code", "Pytest unit test suite validating fix"),
            ("test_result", "Sandbox test execution status & duration"),
            ("retry_count", "Loop counter for self-healing cycle"),
            ("max_retries", "Maximum self-healing attempts guard (default: 3)"),
            ("git_branch", "Generated feature branch name"),
            ("git_diff", "Unified git diff comparing original vs patch"),
            ("pr_title", "Conventional pull request title"),
            ("pr_body", "Institutional markdown PR description with test badges"),
            ("status", "Lifecycle status: analyzing, self_healing, verified, escalated"),
            ("node_history", "Trace of executed state nodes"),
            ("cache_hit", "Boolean flag indicating 0-cost AST cache hit"),
            ("cost_metrics", "Token count, USD cost, and cost savings telemetry")
        ]
        for field, doc in state_fields:
            key_id = f"state_key::{field}"
            self.add_node(key_id, field, "state_key", "src/state.py", docstring=doc)
            self.add_edge("class::src/state.py::AgentState", key_id, "DEFINES_FIELD")

    def _add_langgraph_transitions(self):
        transitions = [
            ("node::START", "node::retrieve_memory_node", "TRANSITIONS_TO"),
            ("node::retrieve_memory_node", "node::symbolic_ast_node", "TRANSITIONS_TO"),
            ("node::symbolic_ast_node", "node::git_pr_node", "BYPASSES_ON_CACHE_HIT"),
            ("node::symbolic_ast_node", "node::security_audit_node", "TRANSITIONS_TO"),
            ("node::security_audit_node", "node::complexity_profiler_node", "TRANSITIONS_TO"),
            ("node::complexity_profiler_node", "node::patch_synthesizer_node", "TRANSITIONS_TO"),
            ("node::patch_synthesizer_node", "node::sandbox_verifier_node", "TRANSITIONS_TO"),
            ("node::sandbox_verifier_node", "node::self_healing_reflection_node", "LOOPS_ON_TEST_FAILURE"),
            ("node::self_healing_reflection_node", "node::sandbox_verifier_node", "RE_EXECUTES_TESTS"),
            ("node::sandbox_verifier_node", "node::git_pr_node", "TRANSITIONS_ON_PASS"),
            ("node::git_pr_node", "node::END", "TERMINATES")
        ]
        for src, tgt, rel in transitions:
            self.add_node(src, src.replace("node::", "").replace("_node", ""), "langgraph_node", "src/graph.py")
            self.add_node(tgt, tgt.replace("node::", "").replace("_node", ""), "langgraph_node", "src/graph.py")
            self.add_edge(src, tgt, rel)

    def export_graph_json(self, output_path: str):
        # Resolve target degrees for any implicit targets
        graph_data = {
            "version": "1.0.0",
            "generator": "CogniCode-Graphify-Engine",
            "statistics": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "categories": dict(defaultdict(int, {
                    cat: sum(1 for n in self.nodes.values() if n["category"] == cat)
                    for cat in NODE_CATEGORIES
                }))
            },
            "nodes": list(self.nodes.values()),
            "edges": self.edges
        }
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2)
        print(f"✅ Exported graph.json ({len(self.nodes)} nodes, {len(self.edges)} edges) -> {output_path}")

    def export_graph_report_md(self, output_path: str):
        # Sort nodes by total degree to find God Nodes
        sorted_nodes = sorted(self.nodes.values(), key=lambda x: x.get("total_degree", 0), reverse=True)
        god_nodes = [n for n in sorted_nodes if n.get("total_degree", 0) >= 6][:10]

        report = f"""# CogniCode Knowledge Graph Architecture & Memory Report
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
- **Total Entities (Nodes):** {len(self.nodes)}
- **Total Relationships (Edges):** {len(self.edges)}
- **Node Breakdown:**
"""
        for cat, count in sorted(self.nodes.items()):
            pass
        
        counts = defaultdict(int)
        for n in self.nodes.values():
            counts[n["category"]] += 1
        for cat, cnt in sorted(counts.items()):
            report += f"  - **{cat.replace('_', ' ').title()}:** {cnt}\n"

        report += f"""
---

## 👑 Central Architectural Hubs ("God Nodes")
These nodes have the highest connectivity and form the backbone of the system:

| Node ID | Category | Total Degree | In-Degree | Out-Degree | Role / File |
| :--- | :--- | :---: | :---: | :---: | :--- |
"""
        for gn in god_nodes:
            report += f"| `{gn['label']}` | `{gn['category']}` | **{gn['total_degree']}** | {gn['in_degree']} | {gn['out_degree']} | `{gn['file']}` |\n"

        report += f"""
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
"""
        modules = [n for n in self.nodes.values() if n["category"] in ("module", "ui")]
        for mod in sorted(modules, key=lambda x: x["file"]):
            doc = mod["docstring"] or "Core module component"
            report += f"- **`{mod['file']}`**: {doc}\n"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ Exported GRAPH_REPORT.md -> {output_path}")

    def export_graph_html(self, output_path: str):
        vis_nodes = []
        for n in self.nodes.values():
            cat_cfg = NODE_CATEGORIES.get(n["category"], {"color": "#888888", "shape": "dot", "size": 15})
            vis_nodes.append({
                "id": n["id"],
                "label": n["label"],
                "title": f"<b>{n['label']}</b><br>Category: {n['category']}<br>File: {n['file']}<br>Total Degree: {n.get('total_degree', 0)}<br><i>{n['docstring'][:120]}</i>",
                "color": cat_cfg["color"],
                "shape": cat_cfg["shape"],
                "size": cat_cfg["size"],
                "category": n["category"],
                "file": n["file"],
                "docstring": n["docstring"]
            })

        vis_edges = []
        for e in self.edges:
            color = "#ff9900" if "CACHE" in e["relationship"] else ("#e74c3c" if "HEAL" in e["relationship"] else "#4a90e2")
            vis_edges.append({
                "from": e["source"],
                "to": e["target"],
                "label": e["relationship"],
                "arrows": "to",
                "font": {"size": 10, "color": "#aaaaaa", "align": "middle"},
                "color": {"color": color, "opacity": 0.7}
            })

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CogniCode Knowledge Graph (Graphify Memory)</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #0e1117;
            color: #f0f6fc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            overflow: hidden;
        }}
        #header {{
            position: absolute;
            top: 10px;
            left: 15px;
            z-index: 100;
            background: rgba(22, 27, 34, 0.85);
            backdrop-filter: blur(8px);
            padding: 12px 18px;
            border-radius: 10px;
            border: 1px solid #30363d;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            max-width: 420px;
        }}
        h2 {{
            margin: 0 0 6px 0;
            font-size: 16px;
            color: #58a6ff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        p {{
            margin: 0 0 10px 0;
            font-size: 12px;
            color: #8b949e;
            line-height: 1.4;
        }}
        #search {{
            width: 100%;
            padding: 7px 10px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #fff;
            font-size: 12px;
            box-sizing: border-box;
            outline: none;
        }}
        #search:focus {{
            border-color: #58a6ff;
        }}
        #legend {{
            margin-top: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 11px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        #network {{
            width: 100vw;
            height: 100vh;
        }}
        #inspector {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            z-index: 100;
            background: rgba(22, 27, 34, 0.9);
            backdrop-filter: blur(8px);
            padding: 14px 18px;
            border-radius: 10px;
            border: 1px solid #30363d;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            width: 320px;
            display: none;
        }}
        #inspector h3 {{
            margin: 0 0 6px 0;
            font-size: 14px;
            color: #58a6ff;
        }}
        #inspector .detail {{
            font-size: 12px;
            color: #c9d1d9;
            margin-bottom: 4px;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h2>🕸️ CogniCode Architectural Graph</h2>
        <p>Graphify Persistent Memory • {len(vis_nodes)} Entities • {len(vis_edges)} Relationships</p>
        <input type="text" id="search" placeholder="🔍 Search nodes (e.g. AgentState, cache, git_pr)...">
        <div id="legend">
            <div class="legend-item"><span class="legend-dot" style="background:#4a90e2"></span>Module</div>
            <div class="legend-item"><span class="legend-dot" style="background:#e67e22"></span>LangGraph Node</div>
            <div class="legend-item"><span class="legend-dot" style="background:#1abc9c"></span>State Key</div>
            <div class="legend-item"><span class="legend-dot" style="background:#9b59b6"></span>Class</div>
            <div class="legend-item"><span class="legend-dot" style="background:#2ecc71"></span>Function</div>
            <div class="legend-item"><span class="legend-dot" style="background:#e74c3c"></span>Prompt</div>
        </div>
    </div>

    <div id="inspector">
        <h3 id="insp-title">Node Inspector</h3>
        <div class="detail"><strong>Category:</strong> <span id="insp-cat"></span></div>
        <div class="detail"><strong>File:</strong> <span id="insp-file"></span></div>
        <div class="detail"><strong>Docstring:</strong> <span id="insp-doc"></span></div>
    </div>

    <div id="network"></div>

    <script type="text/javascript">
        const rawNodes = {json.dumps(vis_nodes)};
        const rawEdges = {json.dumps(vis_edges)};

        const nodes = new vis.DataSet(rawNodes);
        const edges = new vis.DataSet(rawEdges);

        const container = document.getElementById('network');
        const data = {{ nodes: nodes, edges: edges }};
        const options = {{
            nodes: {{
                font: {{ color: '#f0f6fc', size: 12, face: 'monospace' }},
                borderWidth: 1.5,
                shadow: true
            }},
            edges: {{
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.8 }} }},
                smooth: {{ type: 'cubicBezier', forceDirection: 'horizontal', roundness: 0.4 }}
            }},
            physics: {{
                stabilization: {{ iterations: 200 }},
                barnesHut: {{
                    gravitationalConstant: -3500,
                    centralGravity: 0.25,
                    springLength: 95,
                    springConstant: 0.04
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                navigationButtons: true,
                keyboard: true
            }}
        }};

        const network = new vis.Network(container, data, options);

        // Node Click Inspector
        network.on("click", function (params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                document.getElementById('insp-title').innerText = node.label;
                document.getElementById('insp-cat').innerText = node.category;
                document.getElementById('insp-file').innerText = node.file;
                document.getElementById('insp-doc').innerText = node.docstring || "No docstring provided.";
                document.getElementById('inspector').style.display = 'block';
            }} else {{
                document.getElementById('inspector').style.display = 'none';
            }}
        }});

        // Search Filter
        document.getElementById('search').addEventListener('input', function(e) {{
            const val = e.target.value.toLowerCase().trim();
            if (!val) {{
                network.fit();
                return;
            }}
            const matched = rawNodes.find(n => n.label.toLowerCase().includes(val) || n.id.toLowerCase().includes(val));
            if (matched) {{
                network.focus(matched.id, {{
                    scale: 1.2,
                    animation: {{ duration: 500, easingFunction: 'easeInOutQuad' }}
                }});
                network.selectNodes([matched.id]);
            }}
        }});
    </script>
</body>
</html>
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✅ Exported graph.html -> {output_path}")

def run_graphify():
    print("🚀 Running CogniCode-Graphify Codebase Knowledge Graph Extraction...")
    extractor = CodebaseGraphExtractor(PROJECT_ROOT)
    extractor.scan_project()
    extractor.export_graph_json(os.path.join(OUTPUT_DIR, "graph.json"))
    extractor.export_graph_report_md(os.path.join(OUTPUT_DIR, "GRAPH_REPORT.md"))
    extractor.export_graph_html(os.path.join(OUTPUT_DIR, "graph.html"))
    print("🎉 Graphify extraction complete! All artifacts ready in graphify-out/")

if __name__ == "__main__":
    run_graphify()
