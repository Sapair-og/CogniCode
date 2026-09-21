from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """
    Unified typed state contract for the CogniCode multi-agent graph.
    Acts as the Single Source of Truth passed across all LangGraph nodes.
    """
    # Input code details
    source_code: str
    filename: str
    language: str
    
    # Symbolic AST static analysis results
    ast_analysis: Dict[str, Any]
    
    # Few-shot episodic memory retrieval from FAISS
    retrieved_patterns: List[Dict[str, Any]]
    
    # Multi-agent analysis reports
    security_report: Dict[str, Any]
    complexity_report: Dict[str, Any]
    quality_report: Dict[str, Any]
    
    # Code generation & self-healing test harness
    candidate_patch: str
    test_code: str
    test_result: Dict[str, Any]
    
    # Cyclic loop guards
    retry_count: int
    max_retries: int
    
    # Git & GitHub PR automation
    git_branch: str
    git_diff: str
    commit_message: str
    pr_title: str
    pr_body: str
    pr_url: Optional[str]
    
    # Lifecycle & UI visualization
    status: str  # 'analyzing' | 'self_healing' | 'verified' | 'escalated'
    node_history: List[str]
    
    # Token economics & cost optimization
    cache_hit: bool
    cost_metrics: Dict[str, Any]
    
    # TypeSafe AI Jev (System One) fast evaluation
    jev_triage: Dict[str, Any]

