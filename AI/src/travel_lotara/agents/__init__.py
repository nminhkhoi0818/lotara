# Agent module initialization
# Import root_agent when needed using:
#   from src.travel_lotara.agents.root_agent import root_agent
# 
# Do not import it here to avoid triggering agent creation during module imports
from .prompt_manager import register_all_prompts

__all__ = ["register_all_prompts"]