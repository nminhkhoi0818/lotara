from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool



class AgentConfig(BaseModel):
    model: str = Field(
        default="gemini-2.5-flash",
        description="Model Id to use for the agent (e.g., gemini-2.5-flash)"
    )
    name: str = Field(
        default="default_agent",
        description="Name of the agent"
    )
    description: str = Field(
        default="A generic agent",
        description="Description of the agent's purpose"
    )
    instruction: str = Field(
        default="You are an AI agent.",
        description="Instructions guiding the agent's behavior"
    )
    tools : Optional[list[AgentTool]] = Field(
        default=None,
        description="List of tools available to the agent"
    )
    disallow_transfer_to_parent: Optional[bool] = Field(
        default=False,
        description="Whether to disallow transferring tasks to a parent agent"
    )
    disallow_transfer_to_peers: Optional[bool] = Field(
        default=False,
        description="Whether to disallow transferring tasks to peer agents"
    )
    output_key: str = Field(
        default="output",
        description="Key under which the agent's output will be stored"
    )
    output_schema: Optional[Type[BaseModel]] = Field(
        default=None,
        description="Pydantic schema class for the agent's structured output"
    )

class BaseAgent:
    def __init__(self, config: AgentConfig) -> None:
        """Initialize the agent with the given configuration."""
        self.config = config

        self.model_name = config.model
        self.name = config.name
        self.description = config.description
        self.instruction = config.instruction
        self.disallow_transfer_to_parent = config.disallow_transfer_to_parent
        self.disallow_transfer_to_peers = config.disallow_transfer_to_peers
        self.output_key = config.output_key
        self.output_schema = config.output_schema


    @abstractmethod
    def create_agent(self) -> Agent:
        """Create an agent with the given configuration."""
        return Agent(
            model=self.model_name,
            name=self.name,
            description=self.description,
            instruction=self.instruction,
            disallow_transfer_to_parent=self.disallow_transfer_to_parent,
            disallow_transfer_to_peers=self.disallow_transfer_to_peers,
            output_key=self.output_key,
            output_schema=self.output_schema,
        )
    

        