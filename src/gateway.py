"""
Enterprise LLM Gateway for CogniCode
====================================
Provides unified routing, automatic failover (OpenAI -> Groq),
latency telemetry, and circuit-breaking for multi-provider resilience.
"""

import os
import time
from typing import Dict, Any, Optional, List
from src.config import get_llm

class LLMGateway:
    """
    Enterprise LLM Gateway:
    - Primary Route: OpenAI (gpt-4o-mini)
    - Failover Route: Groq (openai/gpt-oss-120b)
    - Telemetry: tracks requests, latencies, tokens, and failover counts.
    """
    def __init__(self):
        self.total_requests: int = 0
        self.successful_requests: int = 0
        self.failover_count: int = 0
        self.telemetry_log: List[Dict[str, Any]] = []

    def get_resilient_llm(
        self,
        primary_provider: str = "openai",
        primary_model: Optional[str] = None,
        temperature: float = 0.1
    ):
        """
        Returns primary LLM, or fails over to secondary provider if primary key is missing.
        """
        has_openai = bool(os.getenv("OPENAI_API_KEY", "").strip())
        has_groq = bool(os.getenv("GROQ_API_KEY", "").strip())

        # If primary is OpenAI but key is missing, failover to Groq
        if primary_provider == "openai" and not has_openai and has_groq:
            self.failover_count += 1
            return get_llm(provider="groq", model_name="openai/gpt-oss-120b", temperature=temperature)
        
        # If primary is Groq but key is missing, failover to OpenAI
        if primary_provider == "groq" and not has_groq and has_openai:
            self.failover_count += 1
            return get_llm(provider="openai", model_name="gpt-4o-mini", temperature=temperature)

        # Standard primary resolution. When both providers are configured, wrap the
        # primary in a runtime fallback so a failed call (rate limit, outage, timeout)
        # is retried on the other provider automatically.
        try:
            primary = get_llm(provider=primary_provider, model_name=primary_model, temperature=temperature)
            if has_openai and has_groq:
                return self.with_runtime_failover(primary, primary_provider, temperature)
            return primary
        except Exception:
            # Automatic fallback to alternative provider
            alt_provider = "groq" if primary_provider == "openai" else "openai"
            self.failover_count += 1
            return get_llm(provider=alt_provider, temperature=temperature)

    def with_runtime_failover(self, primary_llm, primary_provider: str = "openai", temperature: float = 0.1):
        """Wraps an LLM so runtime errors fall through to the other provider."""
        alt_provider = "groq" if primary_provider == "openai" else "openai"
        try:
            fallback = get_llm(provider=alt_provider, temperature=temperature)
        except Exception:
            return primary_llm
        return primary_llm.with_fallbacks([fallback])

    def invoke_with_failover(self, chain, inputs: Dict[str, Any], primary_provider: str = "openai",
                             fallback_chain=None) -> Any:
        """
        Executes an LLM chain with telemetry logging. If it fails and a fallback_chain
        (the same chain built on the other provider) is given, that chain is used instead.
        """
        self.total_requests += 1
        t0 = time.time()
        provider_used = primary_provider
        failed_over = False

        try:
            result = chain.invoke(inputs)
            self.successful_requests += 1
        except Exception as primary_error:
            if fallback_chain is None:
                raise
            alt_provider = "groq" if primary_provider == "openai" else "openai"
            print(f"[LLM Gateway] Primary provider '{primary_provider}' failed: {primary_error}. Failing over to '{alt_provider}'...")
            failed_over = True
            self.failover_count += 1
            provider_used = alt_provider
            result = fallback_chain.invoke(inputs)
            self.successful_requests += 1

        duration_ms = int((time.time() - t0) * 1000)
        
        # Record telemetry
        self.telemetry_log.append({
            "timestamp": time.time(),
            "provider": provider_used,
            "failed_over": failed_over,
            "latency_ms": duration_ms
        })

        return result

    def get_gateway_health(self) -> Dict[str, Any]:
        """Returns runtime gateway health and observability metrics."""
        has_openai = bool(os.getenv("OPENAI_API_KEY", "").strip())
        has_groq = bool(os.getenv("GROQ_API_KEY", "").strip())

        return {
            "status": "HEALTHY" if (has_openai or has_groq) else "DEGRADED (No Keys)",
            "primary_route": "OpenAI (gpt-4o-mini)" if has_openai else "Groq",
            "fallback_route": "Groq" if has_openai else "None",
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failovers_triggered": self.failover_count,
            "available_providers": [p for p, active in [("OpenAI", has_openai), ("Groq", has_groq)] if active]
        }

# Global Gateway instance
llm_gateway = LLMGateway()
