"""Prompt Templates Module - Production-ready prompts for AI assistant."""

from .base_system import BASE_SYSTEM_PROMPT
from .banking import BANKING_MODULE_PROMPT
from .travel import TRAVEL_MODULE_PROMPT
from .research import RESEARCH_MODULE_PROMPT
from .communication import COMMUNICATION_MODULE_PROMPT
from .stocks import STOCKS_MODULE_PROMPT

__all__ = [
    "BASE_SYSTEM_PROMPT",
    "BANKING_MODULE_PROMPT",
    "TRAVEL_MODULE_PROMPT",
    "RESEARCH_MODULE_PROMPT",
    "COMMUNICATION_MODULE_PROMPT",
    "STOCKS_MODULE_PROMPT"
]


def get_prompt_for_module(module_name: str) -> str:
    """
    Get the appropriate prompt template for a given module.
    
    Args:
        module_name: Name of the module (banking, travel, research, etc.)
        
    Returns:
        Combined system prompt with module-specific instructions
    """
    module_prompts = {
        "banking": BANKING_MODULE_PROMPT,
        "travel": TRAVEL_MODULE_PROMPT,
        "research": RESEARCH_MODULE_PROMPT,
        "communication": COMMUNICATION_MODULE_PROMPT,
        "stocks": STOCKS_MODULE_PROMPT
    }
    
    module_prompt = module_prompts.get(module_name.lower(), "")
    return f"{BASE_SYSTEM_PROMPT}\n\n{module_prompt}"
