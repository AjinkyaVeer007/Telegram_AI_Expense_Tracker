"""Graph nodes. Each takes the state and returns a partial state update."""

import json
import logging

from langchain_core.messages import SystemMessage, ToolMessage

from tracker.agent.state import ExpenseState
from tracker.database import save_transaction
from tracker.llm import llm
from tracker.models import Transaction
from tracker.prompts import build_agent_system_prompt
from tracker.tools import ALL_TOOLS

logger = logging.getLogger(__name__)

agent_llm = llm.bind_tools(ALL_TOOLS)


def expense_tracker_agent(state: ExpenseState) -> dict:
    # Keep the full message history: every ToolMessage must follow the
    # AIMessage that contains its tool_call.
    system = SystemMessage(content=build_agent_system_prompt(state.get("image_path")))
    response = agent_llm.invoke([system, *state.get("messages", [])])
    return {"messages": [response]}


def process_tool_result(state: ExpenseState) -> dict:
    """Parse a transaction tool's output into state['transaction']."""
    last_message = state["messages"][-1]
    if not isinstance(last_message, ToolMessage):
        return {}

    try:
        content = last_message.content
        data = json.loads(content) if isinstance(content, str) else content

        if data.get("type") == "error":
            return {"validation_error": data.get("error", "Tool execution failed.")}

        if data.get("type") == "transaction":
            transaction = Transaction(**data["data"])
            logger.info("Transaction extracted: %s", transaction.model_dump())
            return {"transaction": transaction, "validation_error": None}

        return {}
    except Exception as exc:
        logger.exception("Could not process tool result")
        return {"validation_error": f"Unable to process tool result: {exc}"}


def validate_transaction(state: ExpenseState) -> dict:
    transaction = state.get("transaction")

    if transaction is None:
        return {"validation_error": "Transaction information is missing."}
    if transaction.amount <= 0:
        return {"validation_error": "Transaction amount must be greater than zero."}
    if not transaction.purpose.strip():
        return {"validation_error": "Transaction purpose is missing."}

    logger.info("Validation successful")
    return {"validation_error": None}


def save_to_mongodb(state: ExpenseState) -> dict:
    transaction = state.get("transaction")
    if transaction is None:
        return {"validation_error": "No transaction to save."}

    try:
        saved_id = save_transaction(transaction)
    except Exception:
        # Details go to the log, not to the chat.
        logger.exception("MongoDB save failed")
        return {
            "validation_error": "Could not save the transaction to the database. Please try again."
        }

    logger.info("Transaction saved, MongoDB id: %s", saved_id)
    return {"saved_id": saved_id}
