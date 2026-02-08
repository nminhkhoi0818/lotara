"""
Guardrails for Travel Lotara ADK Agents

Provides input/output validation using Google ADK's callback system.

Usage:
    from travel_lotara.guardrails import (
        apply_guardrails_to_agent,
        input_guardrail_callback,
        output_guardrail_callback,
        validate_user_input,
        validate_model_output,
    )
    
    # Apply to an agent
    agent = apply_guardrails_to_agent(my_agent)
    
    # Or use callbacks directly
    agent = LlmAgent(
        ...,
        before_model_callback=input_guardrail_callback,
        after_model_callback=output_guardrail_callback,
    )
"""



from .features import (
    input_intent_guard,
    tool_argument_guard,
)

__all__ = [
    "input_intent_guard",
    "tool_argument_guard",
]
