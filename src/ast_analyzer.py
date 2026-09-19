import ast
from typing import Dict, Any, List

class SymbolicASTAnalyzer(ast.NodeVisitor):
    """
    Symbolic AST Analyzer for deterministic static inspection of Python code.
    Extracts structural invariants, complexity metrics, and flaggable anti-patterns.
    """
    def __init__(self):
        self.functions: List[Dict[str, Any]] = []
        self.classes: List[str] = []
        self.imports: List[str] = []
        self.risky_calls: List[Dict[str, Any]] = []
        self.bare_excepts: List[int] = []
        self.recursive_calls: List[str] = []
        self.cyclomatic_complexity: int = 1
        self._current_function = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        prev_func = self._current_function
        self._current_function = node.name
        
        args = [arg.arg for arg in node.args.args]
        has_docstring = ast.get_docstring(node) is not None
        
        self.functions.append({
            "name": node.name,
            "args": args,
            "line": node.lineno,
            "has_docstring": has_docstring
        })
        self.generic_visit(node)
        self._current_function = prev_func

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes.append(node.name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        mod = node.module or ""
        for alias in node.names:
            self.imports.append(f"{mod}.{alias.name}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Detect eval / exec / dangerous calls
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in ("eval", "exec", "compile"):
                self.risky_calls.append({
                    "function": func_name,
                    "line": node.lineno,
                    "type": "dangerous_builtin"
                })
            # Check for recursion
            if self._current_function and func_name == self._current_function:
                self.recursive_calls.append(func_name)
                
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Bare except (catch all)
        if node.type is None:
            self.bare_excepts.append(node.lineno)
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_If(self, node: ast.If):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

def analyze_code_ast(source_code: str) -> Dict[str, Any]:
    """
    Parses code into an AST, performs deterministic structural analysis,
    and returns a structured dictionary for the AgentState.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {
            "syntax_valid": False,
            "syntax_error": {
                "message": e.msg,
                "line": e.lineno,
                "offset": e.offset,
                "text": e.text
            },
            "functions": [],
            "classes": [],
            "imports": [],
            "risky_calls": [],
            "bare_excepts": [],
            "recursive_calls": [],
            "cyclomatic_complexity": 0,
            "total_ast_nodes": 0
        }

    analyzer = SymbolicASTAnalyzer()
    analyzer.visit(tree)
    
    total_nodes = sum(1 for _ in ast.walk(tree))

    return {
        "syntax_valid": True,
        "syntax_error": None,
        "functions": analyzer.functions,
        "classes": analyzer.classes,
        "imports": analyzer.imports,
        "risky_calls": analyzer.risky_calls,
        "bare_excepts": analyzer.bare_excepts,
        "recursive_calls": list(set(analyzer.recursive_calls)),
        "cyclomatic_complexity": analyzer.cyclomatic_complexity,
        "total_ast_nodes": total_nodes
    }
