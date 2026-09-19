import json
from typing import List, Dict, Any

# Enterprise CWE and Algorithmic Vulnerability Pattern Bank
ENTERPRISE_PATTERNS = [
    {
        "id": "CWE-89",
        "title": "Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')",
        "category": "Security / OWASP A03:2021-Injection",
        "description": "User-controlled input is directly formatted or concatenated into an SQL string without parameterization.",
        "detection_keywords": ["SELECT", "FROM", "WHERE", "cursor.execute", "f\"", "%s", "format", "sqlite3", "psycopg2"],
        "remediation_pattern": "Use parameterized queries with placeholders (? or %s) passing parameters as a tuple, or use an ORM.",
        "example_vulnerable": "cursor.execute(f'SELECT * FROM users WHERE username = \"{user_input}\"')",
        "example_remediated": "cursor.execute('SELECT * FROM users WHERE username = ?', (user_input,))"
    },
    {
        "id": "CWE-400",
        "title": "Uncontrolled Resource Consumption ('Exponential Algorithmic Bottleneck')",
        "category": "Performance & Algorithmic Complexity",
        "description": "Recursive function without memoization causing O(2^N) time complexity and stack overflow.",
        "detection_keywords": ["def", "return", "fibonacci", "recursion", "memo", "cache", "exponential"],
        "remediation_pattern": "Apply @functools.lru_cache, an explicit memoization dictionary, or rewrite as an iterative dynamic programming loop O(N).",
        "example_vulnerable": "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)",
        "example_remediated": "def fib(n, memo={}):\n    if n in memo: return memo[n]\n    if n <= 1: return n\n    memo[n] = fib(n-1, memo) + fib(n-2, memo)\n    return memo[n]"
    },
    {
        "id": "CWE-798",
        "title": "Use of Hard-coded Credentials",
        "category": "Security / OWASP A07:2021-Identification and Authentication Failures",
        "description": "API keys, passwords, or secret tokens hardcoded directly in source code.",
        "detection_keywords": ["api_key =", "secret =", "password =", "token =", "Bearer ", "sk-", "aws_secret"],
        "remediation_pattern": "Extract credentials into environment variables accessed via os.environ.get('KEY_NAME').",
        "example_vulnerable": "API_KEY = 'sk-proj-abc123456789xyz'",
        "example_remediated": "import os\nAPI_KEY = os.environ.get('API_KEY', '')"
    },
    {
        "id": "CWE-476",
        "title": "NULL Pointer Dereference / NoneType Attribute Error",
        "category": "Reliability & Exception Safety",
        "description": "Calling methods or attributes on an object that may evaluate to None without prior null-checking.",
        "detection_keywords": ["None", "AttributeError", "user.profile", ".get(", "dict[key]", "object."],
        "remediation_pattern": "Implement defensive guard clauses: if obj is None: return None, or use dict.get() with fallback defaults.",
        "example_vulnerable": "def get_email(user): return user.contact.email",
        "example_remediated": "def get_email(user):\n    if not user or not getattr(user, 'contact', None): return None\n    return user.contact.email"
    },
    {
        "id": "CWE-95",
        "title": "Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')",
        "category": "Security / Remote Code Execution",
        "description": "Using eval() or exec() to evaluate strings containing user inputs, allowing arbitrary code execution.",
        "detection_keywords": ["eval(", "exec(", "compile("],
        "remediation_pattern": "Replace eval() with ast.literal_eval() for data literals, or use strict whitelist dispatch mapping.",
        "example_vulnerable": "result = eval(user_expression)",
        "example_remediated": "import ast\nresult = ast.literal_eval(user_expression)"
    },
    {
        "id": "CWE-703",
        "title": "Improper Check or Handling of Exceptional Conditions (Bare Except)",
        "category": "Reliability & Anti-Patterns",
        "description": "Using bare except: which silently swallows KeyboardInterrupt and SystemExit, masking fatal defects.",
        "detection_keywords": ["except:", "except Exception as e: pass"],
        "remediation_pattern": "Catch explicit exceptions (e.g. ValueError, KeyError) and log or re-raise errors.",
        "example_vulnerable": "try: do_work()\nexcept: pass",
        "example_remediated": "try: do_work()\nexcept (ValueError, KeyError) as e:\n    logger.error(f'Handled failure: {e}')"
    }
]

class EpisodicMemoryBank:
    """
    Episodic Bug Memory Bank using semantic scoring over verified enterprise CWE patterns.
    Provides few-shot in-context learning to guide the LLM patch synthesizer.
    """
    def __init__(self):
        self.patterns = ENTERPRISE_PATTERNS

    def retrieve_relevant_patterns(self, code_snippet: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Retrieves the top-k most relevant vulnerability remediation templates
        based on token and keyword overlap.
        """
        code_lower = code_snippet.lower()
        scored_patterns = []
        
        for pattern in self.patterns:
            score = 0
            for kw in pattern["detection_keywords"]:
                if kw.lower() in code_lower:
                    score += 2
            # Check title / category overlap
            if any(term in code_lower for term in pattern["title"].lower().split()):
                score += 1
                
            scored_patterns.append((score, pattern))
            
        # Sort by relevance score descending
        scored_patterns.sort(key=lambda x: x[0], reverse=True)
        
        # Return top_k patterns
        results = [p[1] for p in scored_patterns[:top_k]]
        return results

# Global singleton
memory_bank = EpisodicMemoryBank()
