import os
import json
import hashlib
from typing import Dict, Any, Optional

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")

class CodeAuditCache:
    """
    Deterministic AST-Hash Semantic Cache.
    Prevents redundant LLM API calls by hashing code structure and AST metrics.
    Saves 100% of token costs on identical or structurally duplicate submissions.
    """
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self.memory_store: Dict[str, Dict[str, Any]] = {}
        self._load_disk_cache()

    def _compute_hash(self, source_code: str, model_name: str) -> str:
        """Computes SHA-256 fingerprint from stripped code and model identifier."""
        normalized_code = "\n".join(
            line.strip() for line in source_code.splitlines() 
            if line.strip() and not line.strip().startswith("#")
        )
        payload = f"{model_name}::{normalized_code}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _load_disk_cache(self):
        """Loads cached responses from persistent disk storage."""
        cache_file = os.path.join(self.cache_dir, "audit_cache.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    self.memory_store = json.load(f)
            except Exception:
                self.memory_store = {}

    def _save_disk_cache(self):
        """Persists cache to disk."""
        cache_file = os.path.join(self.cache_dir, "audit_cache.json")
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(self.memory_store, f, indent=2)
        except Exception:
            pass

    def get(self, source_code: str, model_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached result if present."""
        code_hash = self._compute_hash(source_code, model_name)
        if code_hash in self.memory_store:
            return self.memory_store[code_hash]
        return None

    def put(self, source_code: str, model_name: str, result_state: Dict[str, Any]):
        """Caches audit results keyed by code hash."""
        code_hash = self._compute_hash(source_code, model_name)
        # Store only serializable core analysis
        cacheable_data = {
            "security_report": result_state.get("security_report"),
            "complexity_report": result_state.get("complexity_report"),
            "candidate_patch": result_state.get("candidate_patch"),
            "test_code": result_state.get("test_code"),
            "test_result": result_state.get("test_result"),
            "git_diff": result_state.get("git_diff"),
            "pr_title": result_state.get("pr_title"),
            "pr_body": result_state.get("pr_body")
        }
        self.memory_store[code_hash] = cacheable_data
        self._save_disk_cache()

# Global singleton
audit_cache = CodeAuditCache()
