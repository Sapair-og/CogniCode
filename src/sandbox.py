import os
import sys
import time
import tempfile
import subprocess
from typing import Dict, Any

def run_test_in_sandbox(
    candidate_code: str,
    test_code: str,
    timeout_seconds: int = 10
) -> Dict[str, Any]:
    """
    Executes pytest against the candidate code in an isolated temporary directory.
    Enforces process timeouts and captures full stdout/stderr and failure traces.
    """
    start_time = time.time()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # File paths
        code_file = os.path.join(temp_dir, "solution.py")
        test_file = os.path.join(temp_dir, "test_solution.py")
        
        # Write candidate code
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(candidate_code)
            
        # Ensure test code imports from solution
        # If test doesn't explicitly import solution, prepend import
        prepared_test_code = test_code
        if "from solution import" not in prepared_test_code and "import solution" not in prepared_test_code:
            prepared_test_code = "from solution import *\n" + prepared_test_code

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(prepared_test_code)
            
        # Run pytest via subprocess
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            test_file,
            "-v",
            "--tb=short"
        ]
        
        try:
            process = subprocess.run(
                cmd,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            duration = round(time.time() - start_time, 3)
            passed = (process.returncode == 0)
            stdout = process.stdout
            stderr = process.stderr
            
            # Extract failure trace if failed
            failure_trace = ""
            if not passed:
                failure_trace = stdout if stdout else stderr
                # Focus on the relevant failure section
                if "FAILURES" in failure_trace or "ERRORS" in failure_trace:
                    lines = failure_trace.splitlines()
                    relevant_lines = [l for l in lines if not l.startswith("=")]
                    failure_trace = "\n".join(relevant_lines[-25:])  # last 25 lines of trace
            
            return {
                "passed": passed,
                "exit_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "failure_trace": failure_trace,
                "duration_seconds": duration,
                "timed_out": False
            }
            
        except subprocess.TimeoutExpired:
            duration = round(time.time() - start_time, 3)
            return {
                "passed": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout_seconds} seconds (potential infinite loop or exponential recursion).",
                "failure_trace": f"TimeoutExpired: Process exceeded {timeout_seconds}s limit. Verify recursion or loop bounds.",
                "duration_seconds": duration,
                "timed_out": True
            }
        except Exception as e:
            return {
                "passed": False,
                "exit_code": -2,
                "stdout": "",
                "stderr": str(e),
                "failure_trace": f"SandboxExecutionError: {str(e)}",
                "duration_seconds": round(time.time() - start_time, 3),
                "timed_out": False
            }
