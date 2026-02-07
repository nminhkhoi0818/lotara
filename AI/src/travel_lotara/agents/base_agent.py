from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, Field,  ConfigDict

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool
from google.adk.tools.base_tool import BaseTool
from google.genai import types


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
    tools : Optional[list[AgentTool | FunctionTool | BaseTool]] = Field(
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

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    generate_content_config : Optional[types.GenerateContentConfig] = Field(
        default=None,
        description="Additional configuration for content generation"
    )

class BaseAgent:
    def __init__(self, config: AgentConfig) -> None:
        """Initialize the agent with the given configuration."""
        self.config = config

        self.model_name = config.model
        self.name = config.name
        self.description = config.description
        self.instruction = config.instruction
        self.tools = config.tools or []
        self.disallow_transfer_to_parent = config.disallow_transfer_to_parent
        self.disallow_transfer_to_peers = config.disallow_transfer_to_peers
        self.output_key = config.output_key
        self.output_schema = config.output_schema
        self.generate_content_config = config.generate_content_config


    def create_agent(self) -> Agent:
        """Create an agent with the given configuration."""
        from src.travel_lotara.config.settings import FAST_HTTP_OPTIONS
        
        # Apply optimized generation config if provided, otherwise use fast defaults
        generate_config = self.generate_content_config or types.GenerateContentConfig()
        
        # Apply fast retry options for 429/503 handling (optimized for production)
        # Only override if not already configured
        if not hasattr(generate_config, 'http_options') or generate_config.http_options is None:
            generate_config.http_options = FAST_HTTP_OPTIONS  # Use optimized retry config
        
        return Agent(
            model=self.model_name,
            name=self.name,
            description=self.description,
            instruction=self.instruction,
            tools=self.tools,
            disallow_transfer_to_parent=self.disallow_transfer_to_parent,
            disallow_transfer_to_peers=self.disallow_transfer_to_peers,
            output_key=self.output_key,
            output_schema=self.output_schema,
            generate_content_config=generate_config,
        )
    

        