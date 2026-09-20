from typing import Dict, Any

# Standard Enterprise Pricing (USD per 1 Million tokens)
MODEL_PRICING = {
    "gpt-4o-mini": {
        "input_cost_per_million": 0.15,
        "output_cost_per_million": 0.60
    },
    "gpt-4o": {
        "input_cost_per_million": 2.50,
        "output_cost_per_million": 10.00
    },
    "groq": {
        "input_cost_per_million": 0.00,
        "output_cost_per_million": 0.00
    }
}

def estimate_tokens(text: str) -> int:
    """
    Fast, deterministic token estimation (~4 characters per token heuristic).
    Avoids requiring heavy tokenizer downloads while providing accurate billing estimates.
    """
    if not text:
        return 0
    return max(1, len(text) // 4)

def calculate_workflow_cost(
    input_text: str,
    output_text: str,
    model_name: str = "gpt-4o-mini",
    is_cached: bool = False
) -> Dict[str, Any]:
    """
    Calculates token counts, estimated cost in USD, and savings achieved via caching/pruning.
    """
    if is_cached:
        baseline_input = estimate_tokens(input_text)
        baseline_output = estimate_tokens(output_text)
        baseline_cost = ((baseline_input / 1_000_000) * 0.15) + ((baseline_output / 1_000_000) * 0.60)
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "cached": True,
            "savings_usd": round(baseline_cost, 6),
            "tokens_saved": baseline_input + baseline_output
        }

    input_tokens = estimate_tokens(input_text)
    output_tokens = estimate_tokens(output_text)
    total_tokens = input_tokens + output_tokens

    pricing = MODEL_PRICING.get(model_name.lower(), MODEL_PRICING["gpt-4o-mini"])
    input_cost = (input_tokens / 1_000_000) * pricing["input_cost_per_million"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_cost_per_million"]
    total_cost = input_cost + output_cost

    return {
        "prompt_tokens": input_tokens,
        "completion_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cost_usd": round(total_cost, 6),
        "cached": False,
        "savings_usd": 0.0,
        "tokens_saved": 0
    }
