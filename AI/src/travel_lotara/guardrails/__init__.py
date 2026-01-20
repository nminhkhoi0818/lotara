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

from travel_lotara.guardrails.callbacks import (
    apply_guardrails_to_agent,
    input_guardrail_callback,
    output_guardrail_callback,
    validate_user_input,
    validate_model_output,
    InputValidationResult,
    OutputValidationResult,
)

__all__ = [
    # Main function
    "apply_guardrails_to_agent",
    # Callbacks
    "input_guardrail_callback",
    "output_guardrail_callback",
    # Validators
    "validate_user_input",
    "validate_model_output",
    # Types
    "InputValidationResult",
    "OutputValidationResult",
]
