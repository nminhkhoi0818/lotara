import json
from google.genai import types
from pydantic import ValidationError

from src.travel_lotara.core.contracts import TravelFinalResponse
from src.travel_lotara.agents.shared_libraries import OutputMessage


def enforce_final_json_output(llm_response: types.Content) -> dict:
    """
    Enforces final JSON output schema.
    Raises ValueError if invalid.
    """

    # Extract raw text
    text = ""
    for part in llm_response.parts:
        if hasattr(part, "text"):
            text += part.text

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Final response is not valid JSON")

    try:
        validated = OutputMessage(**payload)
    except ValidationError as e:
        raise ValueError(f"Final response schema invalid: {e}")

    return validated.model_dump()


