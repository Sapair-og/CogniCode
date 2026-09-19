import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_HEALING_RETRIES = 3

def get_llm(
    provider: str = "openai",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.1
):
    """
    Factory function returning a configured LangChain ChatModel instance.
    Supports OpenAI (gpt-4o-mini) and Groq (llama-3.3-70b).
    """
    provider = provider.lower().strip()
    
    if provider == "groq":
        from langchain_groq import ChatGroq
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY not found. Please provide it in the UI or .env file.")
        model = model_name or DEFAULT_GROQ_MODEL
        return ChatGroq(
            api_key=key,
            model=model,
            temperature=temperature
        )
    else:
        # Default to OpenAI
        from langchain_openai import ChatOpenAI
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not found. Please provide it in the UI or .env file.")
        model = model_name or DEFAULT_OPENAI_MODEL
        return ChatOpenAI(
            api_key=key,
            model=model,
            temperature=temperature
        )
