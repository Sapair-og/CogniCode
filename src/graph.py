from typing import Literal
from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes import (
    retrieve_memory_node,
    symbolic_ast_node,
    security_audit_node,
    complexity_profiler_node,
    patch_synthesizer_node,
    sandbox_verifier_node,
    self_healing_reflection_node,
    git_pr_node
)

def check_cache_bypass(state: AgentState) -> Literal["git_pr", "security_audit"]:
    """
    Cost & Latency Optimization Edge:
    If AST semantic cache hit occurs, bypass LLM nodes straight to PR formulation.
    """
    if state.get("cache_hit", False):
        return "git_pr"
    return "security_audit"

def should_self_heal(state: AgentState) -> Literal["self_healing_reflection", "git_pr"]:
    """
    Conditional edge function deciding whether to trigger self-healing
    or proceed to Git PR formulation.
    """
    test_result = state.get("test_result", {})
    passed = test_result.get("passed", False)
    retries = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)
    
    # If tests pass, proceed straight to Git PR
    if passed:
        return "git_pr"
        
    # If tests failed but we have retries remaining, loop to self-healing
    if retries < max_retries:
        return "self_healing_reflection"
        
    # If tests failed and retries exhausted, escalate to Git PR with review warning
    return "git_pr"

def build_cognicode_graph() -> StateGraph:
    """
    Assembles and compiles the CogniCode stateful cyclic agent graph.
    """
    builder = StateGraph(AgentState)
    
    # Add Nodes
    builder.add_node("retrieve_memory", retrieve_memory_node)
    builder.add_node("symbolic_ast", symbolic_ast_node)
    builder.add_node("security_audit", security_audit_node)
    builder.add_node("complexity_profiler", complexity_profiler_node)
    builder.add_node("patch_synthesizer", patch_synthesizer_node)
    builder.add_node("sandbox_verifier", sandbox_verifier_node)
    builder.add_node("self_healing_reflection", self_healing_reflection_node)
    builder.add_node("git_pr", git_pr_node)
    
    # Linear Pre-Execution Pipeline with Cache Bypass
    builder.add_edge(START, "retrieve_memory")
    builder.add_edge("retrieve_memory", "symbolic_ast")
    builder.add_conditional_edges(
        "symbolic_ast",
        check_cache_bypass,
        {
            "git_pr": "git_pr",
            "security_audit": "security_audit"
        }
    )
    builder.add_edge("security_audit", "complexity_profiler")
    builder.add_edge("complexity_profiler", "patch_synthesizer")
    builder.add_edge("patch_synthesizer", "sandbox_verifier")
    
    # Cyclic Verification & Self-Healing Loop
    builder.add_conditional_edges(
        "sandbox_verifier",
        should_self_heal,
        {
            "self_healing_reflection": "self_healing_reflection",
            "git_pr": "git_pr"
        }
    )
    
    # Loop back from Self-Healing to Sandbox execution
    builder.add_edge("self_healing_reflection", "sandbox_verifier")
    
    # Terminal Edge
    builder.add_edge("git_pr", END)
    
    # Compile the graph
    app = builder.compile()
    return app

# Singleton compiled instance
cognicode_graph = build_cognicode_graph()
