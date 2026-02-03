"""
Opik Prompt Management for Travel Lotara Agents.

This module provides centralized prompt management with Opik integration,
including versioning, metadata tracking, and tracing integration.

Usage:
    from src.travel_lotara.agents.prompt_manager import prompt_manager
    
    # Get a prompt
    prompt = prompt_manager.get_prompt("root_agent")
    
    # Use in agent
    agent = Agent(instruction=prompt.prompt, ...)
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

try:
    import opik
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    logging.warning("Opik not available - prompt management will use fallback mode")

from src.travel_lotara.config.settings import get_settings

logger = logging.getLogger(__name__)


class PromptManager:
    """
    Manages prompts with Opik integration for versioning and tracking.
    
    Features:
    - Automatic prompt registration with Opik
    - Version management
    - Metadata tracking
    - Integration with tracing
    - Fallback mode when Opik unavailable
    """
    
    def __init__(self):
        """Initialize the prompt manager."""
        self.settings = get_settings()
        self.prompts: Dict[str, Any] = {}  # Cache of Opik prompt objects
        self.prompt_texts: Dict[str, str] = {}  # Fallback prompt storage
        self.prompt_metadata: Dict[str, Dict[str, Any]] = {}
        self.enabled = OPIK_AVAILABLE and self.settings.opik_api_key is not None
        
        if self.enabled:
            logger.info("[Prompt Manager] Opik integration enabled")
        else:
            logger.warning("[Prompt Manager] Running in fallback mode (Opik disabled)")
    
    def register_prompt(
        self,
        agent_name: str,
        prompt_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Register a prompt with Opik.
        
        Args:
            agent_name: Unique identifier for the agent
            prompt_text: The prompt template text
            metadata: Optional metadata (version, description, etc.)
            
        Returns:
            Opik Prompt object if successful, None otherwise
        """
        # Store prompt text for fallback
        self.prompt_texts[agent_name] = prompt_text
        
        # Store metadata
        if metadata:
            self.prompt_metadata[agent_name] = metadata
        
        if not self.enabled:
            logger.debug(f"[Prompt Manager] Registered {agent_name} in fallback mode")
            return None
        
        try:
            # Create Opik prompt name
            prompt_name = f"{agent_name}_prompt"
            
            # Prepare metadata for Opik
            opik_metadata = metadata.copy() if metadata else {}
            opik_metadata.update({
                "agent_name": agent_name,
                "project": self.settings.opik_project_name or "lotara-travel",
                "registered_at": datetime.now().isoformat()
            })
            
            # Create Opik Prompt object
            prompt = opik.Prompt(
                name=prompt_name,
                prompt=prompt_text,
                metadata=opik_metadata
            )
            
            # Cache the prompt
            self.prompts[agent_name] = prompt
            
            logger.info(
                f"[Prompt Manager] Registered '{agent_name}' "
                f"(version: {metadata.get('version', 'unknown')})"
            )
            
            return prompt
            
        except Exception as e:
            logger.error(f"[Prompt Manager] Failed to register {agent_name}: {e}")
            return None
    
    def get_prompt(self, agent_name: str) -> Any:
        """
        Get a prompt by agent name.
        
        Args:
            agent_name: The agent identifier
            
        Returns:
            Opik Prompt object or fallback object with .prompt attribute
        """
        if self.enabled and agent_name in self.prompts:
            return self.prompts[agent_name]
        
        # Fallback: return a simple object with prompt text
        class FallbackPrompt:
            def __init__(self, text: str, metadata: Dict[str, Any]):
                self.prompt = text
                self.metadata = metadata
        
        prompt_text = self.prompt_texts.get(agent_name, "")
        metadata = self.prompt_metadata.get(agent_name, {})
        
        return FallbackPrompt(prompt_text, metadata)
    
    def get_prompt_text(self, agent_name: str) -> str:
        """
        Get the raw prompt text for an agent.
        
        Args:
            agent_name: The agent identifier
            
        Returns:
            The prompt text string
        """
        prompt = self.get_prompt(agent_name)
        return prompt.prompt if hasattr(prompt, 'prompt') else ""
    
    def get_prompt_metadata(self, agent_name: str) -> Dict[str, Any]:
        """
        Get metadata for a prompt.
        
        Args:
            agent_name: The agent identifier
            
        Returns:
            Dictionary of prompt metadata
        """
        return self.prompt_metadata.get(agent_name, {})
    
    def format_prompt(self, agent_name: str, **variables) -> str:
        """
        Format a prompt with variables.
        
        Args:
            agent_name: The agent identifier
            **variables: Variables to substitute in the prompt
            
        Returns:
            Formatted prompt string
        """
        prompt = self.get_prompt(agent_name)
        
        if self.enabled and hasattr(prompt, 'format'):
            return prompt.format(**variables)
        
        # Fallback: simple string formatting
        prompt_text = prompt.prompt if hasattr(prompt, 'prompt') else ""
        return prompt_text.format(**variables)
    
    def list_prompts(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered prompts with their metadata.
        
        Returns:
            Dictionary mapping agent names to their metadata
        """
        return {
            agent_name: {
                "metadata": self.get_prompt_metadata(agent_name),
                "registered": agent_name in self.prompts,
                "has_text": agent_name in self.prompt_texts
            }
            for agent_name in set(list(self.prompts.keys()) + list(self.prompt_texts.keys()))
        }


# Global prompt manager instance
prompt_manager = PromptManager()


def register_all_prompts():
    """
    Register all agent prompts with Opik.
    
    This function should be called explicitly after all imports are complete
    to avoid circular import issues.
    """
    try:
        from src.travel_lotara.agents.prompt import ROOT_AGENT_INSTR, ROOT_AGENT_METADATA
        from src.travel_lotara.agents.sub_agents.inspiration_agent.prompt import (
            INSPIRATION_AGENT_INSTR,
            INSPIRATION_AGENT_METADATA
        )
        from src.travel_lotara.agents.sub_agents.pre_agent.prompt import (
            PRE_AGENT_INSTR,
            PRE_AGENT_METADATA
        )
        from src.travel_lotara.agents.sub_agents.planning_agent.prompt import (
            PLANNING_AGENT_INSTR,
            PLANNING_AGENT_METADATA,
            REFACTORING_OUTPUT_INSTR,
            REFACTORING_OUTPUT_METADATA,
            GOOGLE_SEARCH_INSTR,
            GOOGLE_SEARCH_METADATA
        )
        from src.travel_lotara.agents.sub_agents.formatter_agent.prompt import (
            FORMATTER_AGENT_INSTR,
            FORMATTER_AGENT_METADATA
        )
        
        # Register all prompts
        prompt_manager.register_prompt("root_agent", ROOT_AGENT_INSTR, ROOT_AGENT_METADATA)
        prompt_manager.register_prompt("inspiration_agent", INSPIRATION_AGENT_INSTR, INSPIRATION_AGENT_METADATA)
        prompt_manager.register_prompt("planning_agent", PLANNING_AGENT_INSTR, PLANNING_AGENT_METADATA)
        prompt_manager.register_prompt("refactoring_output_agent", REFACTORING_OUTPUT_INSTR, REFACTORING_OUTPUT_METADATA)
        prompt_manager.register_prompt("google_search_agent", GOOGLE_SEARCH_INSTR, GOOGLE_SEARCH_METADATA)
        prompt_manager.register_prompt("formatter_agent", FORMATTER_AGENT_INSTR, FORMATTER_AGENT_METADATA)
        
        logger.info(f"[Prompt Manager] Registered {len(prompt_manager.list_prompts())} prompts")
    except Exception as e:
        logger.warning(f"[Prompt Manager] Could not register prompts: {e}")


# DO NOT automatically register on import to avoid circular dependencies
# Call register_all_prompts() explicitly after all modules are loaded
