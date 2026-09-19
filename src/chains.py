import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

# Pydantic Schemas for Structured Agent Outputs
class SecurityAuditModel(BaseModel):
    cwe_id: str = Field(description="CWE Identifier, e.g. CWE-89, CWE-400, CWE-798 or 'Clean'")
    owasp_category: str = Field(description="Corresponding OWASP Top 10 category or 'N/A'")
    severity: str = Field(description="Severity rating: CRITICAL, HIGH, MEDIUM, LOW, or SAFE")
    explanation: str = Field(description="Detailed explanation of the vulnerability and security implications")
    vulnerable_lines: List[int] = Field(default_factory=list, description="Line numbers containing the vulnerability")

class ComplexityReportModel(BaseModel):
    time_before: str = Field(description="Asymptotic Big-O time complexity before fix, e.g. O(2^N), O(N^2), O(N)")
    time_after: str = Field(description="Asymptotic Big-O time complexity after proposed fix, e.g. O(N), O(log N)")
    space_before: str = Field(description="Big-O space complexity before fix")
    space_after: str = Field(description="Big-O space complexity after fix")
    analysis: str = Field(description="Detailed algorithmic bottleneck breakdown")
    improvement: str = Field(description="Summary of asymptotic improvement, e.g. 'Exponential to Linear'")

class PatchAndTestModel(BaseModel):
    refactored_code: str = Field(description="Complete, syntactically valid Python code containing the full remediated solution")
    test_code: str = Field(description="Complete pytest test suite with test functions testing both standard and edge cases")
    patch_rationale: str = Field(description="Brief explanation of how the patch solves both security and performance")

class SelfHealingModel(BaseModel):
    error_diagnosis: str = Field(description="Analysis of why the pytest test suite or compilation failed based on the traceback")
    revised_code: str = Field(description="Repaired Python source code resolving the failure")
    revised_test: str = Field(description="Repaired or verified pytest test suite")
    fix_notes: str = Field(description="Explanation of corrections applied")

# Prompts
SECURITY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an Enterprise Security Vulnerability Auditor specializing in OWASP Top 10, CWE patterns, and secure code review.
Analyze the provided code and deterministic AST summary. Cross-reference with the retrieved enterprise pattern bank.
Identify security vulnerabilities, credential leaks, injection risks, or unsafe operations.

You must respond with valid JSON matching this schema:
{
    "cwe_id": "CWE-...",
    "owasp_category": "...",
    "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "SAFE",
    "explanation": "...",
    "vulnerable_lines": [1, 2]
}"""),
    ("human", """Source Code:
```python
{source_code}
```

Symbolic AST Metrics:
{ast_metrics}

Retrieved Enterprise Patterns from Memory Bank:
{retrieved_patterns}
""")
])

COMPLEXITY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Senior Algorithmic Performance Engineer and LeetCode Grandmaster.
Analyze the Big-O time and space complexity of the provided code.
Evaluate recursive calls, loop bounds, memory consumption, and identify asymptotic bottlenecks.

You must respond with valid JSON matching this schema:
{
    "time_before": "O(...)",
    "time_after": "O(...)",
    "space_before": "O(...)",
    "space_after": "O(...)",
    "analysis": "...",
    "improvement": "..."
}"""),
    ("human", """Source Code:
```python
{source_code}
```

AST Function & Recursion Data:
{ast_metrics}
""")
])

PATCH_AND_TEST_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Principal Software Engineer and Test-Driven Development (TDD) specialist.
Your task is to:
1. Write a complete, production-ready, clean Python refactoring of the source code that resolves the security vulnerability and optimizes algorithmic bottlenecks.
2. Write a comprehensive pytest test suite (`test_code`) that verifies the correctness of the refactored code. The tests must import the function from `solution` (e.g. `from solution import func_name`).
3. Make sure the code is 100% syntactically valid and runnable in Python 3.11.

You must respond with valid JSON matching this schema:
{
    "refactored_code": "def func(...): ...",
    "test_code": "import pytest\\nfrom solution import ...\\ndef test_basic(): ...",
    "patch_rationale": "..."
}"""),
    ("human", """Original Source Code:
```python
{source_code}
```

Security Audit Findings:
{security_report}

Algorithmic Profiling Findings:
{complexity_report}

Retrieved Remediation Pattern:
{retrieved_patterns}
""")
])

SELF_HEALING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an Autonomous Self-Healing Debugger operating inside a test-driven CI/CD loop.
The previous patch or test suite FAILED when executed in the Python Pytest sandbox.
Analyze the execution failure trace, identify the root cause (syntax error, assertion failure, missing import, timeout), and repair the code and test suite.

You must respond with valid JSON matching this schema:
{
    "error_diagnosis": "...",
    "revised_code": "def func(...): ...",
    "revised_test": "import pytest\\nfrom solution import ...",
    "fix_notes": "..."
}"""),
    ("human", """Candidate Code That Failed:
```python
{candidate_code}
```

Test Suite That Ran:
```python
{test_code}
```

Sandbox Execution Failure Trace:
```text
{failure_trace}
```

Retry Attempt: {retry_count} of {max_retries}
Repair the implementation so that pytest passes 100%!
""")
])
