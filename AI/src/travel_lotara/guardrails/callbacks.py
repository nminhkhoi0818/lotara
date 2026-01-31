"""
ADK Callbacks for Guardrails

Implements input/output validation using Google ADK's callback system.
These are used with LlmAgent's before_model_callback and after_model_callback.

Reference: https://google.github.io/adk-docs/callbacks/
"""

from __future__ import annotations

import logging
from typing import Any, Optional
from dataclasses import dataclass

from google.adk.agents import LlmAgent
from google.genai import types

logger = logging.getLogger(__name__)


# ============================================
# INPUT GUARDRAILS (before_model_callback)
# ============================================

@dataclass
class InputValidationResult:
    """Result of input validation."""
    is_valid: bool
    blocked_reason: Optional[str] = None
    sanitized_input: Optional[str] = None


BLOCKED_TERMS = [
    "illegal",
    "smuggle",
    "fake passport",
    "evade customs",
]


def validate_user_input(user_input: str) -> InputValidationResult:
    """
    Validate user input before sending to the model.
    
    Checks for:
    - Blocked/harmful content
    - Input length limits
    - Basic sanitization
    """
    if not user_input or not user_input.strip():
        return InputValidationResult(
            is_valid=False,
            blocked_reason="Empty input provided"
        )
    
    # Check for blocked terms
    input_lower = user_input.lower()
    for term in BLOCKED_TERMS:
        if term in input_lower:
            logger.warning(f"Blocked term detected: {term}")
            return InputValidationResult(
                is_valid=False,
                blocked_reason="Your request contains content that cannot be processed."
            )
    
    # Length check (prevent token bombing)
    if len(user_input) > 10000:
        return InputValidationResult(
            is_valid=False,
            blocked_reason="Input too long. Please limit your request to under 10000 characters."
        )
    
    return InputValidationResult(is_valid=True, sanitized_input=user_input.strip())


def input_guardrail_callback(
    callback_context: Any,
    llm_request: Any,
) -> Optional[types.Content]:
    """
    ADK before_model_callback for input validation.
    
    Args:
        callback_context: The ADK callback context
        llm_request: The LLM request being sent
        
    Returns:
        None to continue, or Content to skip model and return directly.
    """
    # Try to extract user input from the llm_request
    user_input = ""
    
    try:
        # Extract from llm_request contents
        if hasattr(llm_request, 'contents') and llm_request.contents:
            for content in llm_request.contents:
                if hasattr(content, 'parts'):
                    for part in content.parts:
                        if hasattr(part, 'text') and part.text:
                            user_input += part.text + " "
    except Exception as e:
        logger.debug(f"Could not extract user input: {e}")
        return None  # Continue if we can't extract
    
    if not user_input.strip():
        return None  # No user input to validate, continue
    
    result = validate_user_input(user_input.strip())
    
    if not result.is_valid:
        # Return a blocked response instead of calling the model
        logger.warning(f"Input blocked: {result.blocked_reason}")
        return types.Content(
            parts=[types.Part(text=f"I'm sorry, I can't help with that request. {result.blocked_reason}")]
        )
    
    return None  # Continue to model


# ============================================
# OUTPUT GUARDRAILS (after_model_callback)
# ============================================

@dataclass
class OutputValidationResult:
    """Result of output validation."""
    is_valid: bool
    issues: list[str]
    confidence: float = 1.0


def validate_model_output(output: str, agent_name: str = "unknown") -> OutputValidationResult:
    """
    Validate model output before returning to user.
    
    Checks for:
    - Hallucination indicators
    - Completeness
    - Safety
    """
    issues = []
    confidence = 1.0
    
    if not output or not output.strip():
        issues.append("Empty response")
        confidence = 0.0
    
    output_lower = output.lower()
    
    # Check for hallucination indicators
    hallucination_phrases = [
        "i don't have access to real-time",
        "i cannot browse the internet",
        "as an ai, i cannot",
        "i'm not able to access external",
    ]
    
    for phrase in hallucination_phrases:
        if phrase in output_lower:
            issues.append(f"Response indicates limitation: {phrase[:30]}...")
            confidence *= 0.7
    
    # Check for incomplete responses
    if output.strip().endswith("...") or output.strip().endswith("and so on"):
        issues.append("Response appears incomplete")
        confidence *= 0.8
    
    # Check for sensitive content that shouldn't be in responses
    sensitive_patterns = [
        "credit card number",
        "social security",
        "password",
    ]
    for pattern in sensitive_patterns:
        if pattern in output_lower:
            issues.append(f"Response may contain sensitive info: {pattern}")
            confidence *= 0.5
    
    return OutputValidationResult(
        is_valid=len(issues) == 0 or confidence >= 0.5,
        issues=issues,
        confidence=confidence,
    )


def output_guardrail_callback(
    callback_context: Any,
    llm_response: Any,
) -> Optional[types.Content]:
    """
    ADK after_model_callback for output validation.
    
    Args:
        callback_context: The ADK callback context
        llm_response: The LLM response received
        
    Returns:
        None to use model output, or Content to override.
    """
    if not llm_response:
        return None
    
    # Extract text from response
    output_text = ""
    try:
        if hasattr(llm_response, 'content') and llm_response.content:
            if hasattr(llm_response.content, 'parts'):
                for part in llm_response.content.parts:
                    if hasattr(part, 'text') and part.text:
                        output_text += part.text
    except Exception as e:
        logger.debug(f"Could not extract output: {e}")
        return None
    
    if not output_text:
        return None
    
    # Get agent name for context-aware validation
    agent_name = "unknown"
    if hasattr(callback_context, 'agent_name'):
        agent_name = callback_context.agent_name
    
    result = validate_model_output(output_text, agent_name)
    
    if not result.is_valid:
        logger.warning(f"Output validation failed for {agent_name}: {result.issues}")
        # Could modify or block response here
        # For now, just log and continue
    
    if result.issues:
        logger.info(f"Output validation issues for {agent_name}: {result.issues}, confidence: {result.confidence}")
    
    return None  # Use the original response


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def apply_guardrails_to_agent(agent: LlmAgent) -> LlmAgent:
    """
    Apply both input and output guardrails to an agent.
    
    Usage:
        agent = apply_guardrails_to_agent(my_agent)
    """
    agent.before_model_callback = input_guardrail_callback
    agent.after_model_callback = output_guardrail_callback
    return agent

