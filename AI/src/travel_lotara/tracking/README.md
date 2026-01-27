# Opik Tracing for Travel Lotara

## Overview

This module provides comprehensive **Opik** integration for tracking and observing your Travel Lotara AI agents using the **official Opik ADK integration**.

**Official Documentation:** https://www.comet.com/docs/opik/integrations/adk

### What Gets Tracked Automatically

- ✅ **Agent executions** - All agents (root + sub-agents)
- ✅ **LLM calls** - Automatic cost tracking for all providers (OpenAI, Anthropic, Google AI, etc.)
- ✅ **Tool invocations** - Arguments, results, duration
- ✅ **Error tracking** - Detailed stack traces
- ✅ **Agent graphs** - Visual Mermaid diagrams
- ✅ **Performance metrics** - Duration for every operation
- ✅ **Hierarchical traces** - Complete parent-child relationships

## Quick Start

### 1. Install Opik

```bash
pip install opik google-adk
# or
uv add opik google-adk
```

### 2. Set API Key

Get your API key from https://www.comet.com/signup

Add to `.env`:
```env
OPIK_API_KEY=your_key_here
OPIK_PROJECT=Lotara
```

### 3. Instrument Your Agent (One Line!)

```python
from travel_lotara.tracking import get_tracer, flush_traces
from google.adk.agents import LlmAgent

# Create your agent
root_agent = LlmAgent(
    name="travel_agent",
    model=llm,
    instruction="...",
    sub_agents=[subagent1, subagent2],  # All will be auto-instrumented!
)

# Instrument agent - this is ALL you need!
tracer = get_tracer()
tracer.instrument_agent(root_agent)  # Uses track_adk_agent_recursive under the hood

# Run your agent - tracing happens automatically!
result = agent.run()

# Flush before exit
flush_traces()
```

### 4. View Traces

Visit: **https://www.comet.com/opik/Lotara/traces**

## How It Works

The integration uses Opik's official `track_adk_agent_recursive()` function which:

1. Automatically adds callbacks to your agent:
   - `before_agent_callback` / `after_agent_callback`
   - `before_model_callback` / `after_model_callback` (with cost tracking)
   - `before_tool_callback` / `after_tool_callback`

2. Recursively instruments ALL sub-agents in the hierarchy

3. Tracks everything automatically with zero additional code

## Key Features

### Automatic Cost Tracking

Opik automatically calculates costs for:
- OpenAI models (GPT-4, GPT-3.5, etc.)
- Anthropic models (Claude)
- Google AI (Gemini)
- AWS Bedrock
- Azure OpenAI
- All LiteLLM-supported models

### Multi-Agent Hierarchies

One call instruments everything:

```python
# This instruments root + ALL sub-agents automatically
tracer.instrument_agent(root_agent)
```

No need to manually add callbacks to each agent!

### Agent Graph Visualization

Opik automatically generates Mermaid diagrams showing:
- Agent hierarchy
- Sequential flows
- Parallel processing
- Tool connections

### Thread Support

For conversational apps with ADK sessions:

```python
from google.adk import sessions

session_service = sessions.InMemorySessionService()
runner = Runner(agent=root_agent, session_service=session_service)

# Session ID automatically becomes thread ID in Opik
session = session_service.create_session_sync(
    app_name="lotara",
    user_id="user_123",
    session_id="conversation_456"
)

# All traces grouped by session!
```

## API Reference

### `OpikTracer`

```python
class OpikTracer:
    def __init__(self)
    def instrument_agent(agent) -> None
    def flush() -> None
```

### Functions

```python
def get_tracer() -> OpikTracer
    """Get singleton tracer instance."""

def flush_traces() -> None
    """Flush all traces before exit."""
```

## Troubleshooting

### No traces appearing?

1. Check API key is set: `echo $OPIK_API_KEY`
2. Ensure you called `tracer.instrument_agent(root_agent)`
3. Call `flush_traces()` before script exits
4. Check Opik console output for errors

### Incomplete traces?

When using `Runner.run_async`, process ALL events:

```python
async for event in runner.run_async(...):
    # Process event
    if event.is_final_response():
        # DON'T break here! Continue processing
        pass
# Loop must complete for traces to be logged
```

### Cost tracking not working?

- Opik automatically tracks costs for known models
- Uses LiteLLM pricing data
- Free/unknown models show $0.00
- See supported models: https://www.comet.com/tracing/supported_models

## Example: Complete Integration

```python
# agents/root_agent.py
from google.adk.agents import LlmAgent
from travel_lotara.tracking import get_tracer

root_agent = LlmAgent(
    name="travel_assistant",
    model=llm,
    sub_agents=[inspiration_agent, planning_agent],
)

# Instrument once at module level
tracer = get_tracer()
tracer.instrument_agent(root_agent)
```

```python
# main.py
from travel_lotara.tracking import flush_traces
from travel_lotara.agents import root_agent

async def main():
    try:
        result = await root_agent.run(user_input)
        print(result)
    finally:
        flush_traces()  # Ensure traces upload

if __name__ == "__main__":
    asyncio.run(main())
```

That's it! All agent, LLM, and tool calls are automatically traced.

## Advanced: Hybrid Tracing

Combine ADK tracing with custom `@track` decorators:

```python
from opik import track

@track(name="custom_processing", tags=["data"])
def process_data(data):
    # This creates a nested span under agent traces
    return processed

# In your tool
def my_tool(input):
    processed = process_data(input)  # Automatically nested in trace!
    return result
```

## Learn More

- **Official Docs:** https://www.comet.com/docs/opik/integrations/adk
- **ADK Guide:** https://google.github.io/adk-docs/
- **Supported Models:** https://www.comet.com/tracing/supported_models
- **Python SDK Ref:** https://www.comet.com/docs/opik/python-sdk-reference

## Credits

Built using Opik's official `track_adk_agent_recursive` integration.
