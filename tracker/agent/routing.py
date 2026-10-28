"""Conditional edge functions."""

from langchain_core.messages import AIMessage, ToolMessage

from tracker.agent.state import ExpenseState
from tracker.tools import TRANSACTION_TOOL_NAMES


def route_agent(state: ExpenseState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tool"
    return "end"


def route_after_tool(state: ExpenseState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, ToolMessage) and last_message.name in TRANSACTION_TOOL_NAMES:
        return "process_transaction"
    # fetch_transactions (and anything else) goes back to the agent
    # so it can read the result and write the analysis.
    return "agent"


def route_validation(state: ExpenseState) -> str:
    return "invalid" if state.get("validation_error") else "valid"
