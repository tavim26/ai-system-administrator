"""ADK agent: a read-only system administrator for the data/ directory."""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import MCPToolset, SseConnectionParams

from .config import MCP_SERVER_URL, MODEL_NAME, SYSTEM_PROMPT
from .guardrail import flag_guard_before_model

AGENT_NAME = "quite_an_agent"
MAX_RESPONSE_TOKENS = 512


def create_agent() -> Agent:
    """Build the agent with the MCP filesystem tools and the flag guardrail."""
    return Agent(
        name=AGENT_NAME,
        description="Read-only system administrator for the data/ directory.",
        model=LiteLlm(
            model=MODEL_NAME,
            temperature=0.0,  # Deterministic answers make the guardrails predictable
            max_tokens=MAX_RESPONSE_TOKENS,
        ),
        instruction=SYSTEM_PROMPT,
        tools=[MCPToolset(connection_params=SseConnectionParams(url=MCP_SERVER_URL))],
        before_model_callback=flag_guard_before_model,
    )


# Entry point discovered by `adk web`
root_agent = create_agent()