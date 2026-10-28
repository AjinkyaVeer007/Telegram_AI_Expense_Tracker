"""Turn a graph result into user-facing text (shared by Telegram bot and CLI)."""

from langchain_core.messages import AIMessage


def last_ai_text(result: dict) -> str:
    for message in reversed(result.get("messages", [])):
        if isinstance(message, AIMessage) and isinstance(message.content, str):
            if message.content.strip():
                return message.content
    return ""


def format_result(result: dict) -> str:
    error = result.get("validation_error")
    if error:
        return f"Could not complete the request:\n{error}"

    saved_id = result.get("saved_id")
    if saved_id:
        transaction = result.get("transaction")
        if transaction:
            return (
                "Expense saved successfully!\n\n"
                f"Amount: ₹{transaction.amount:,}\n"
                f"Purpose: {transaction.purpose}\n"
                f"Category: {transaction.category.value}\n"
                f"Date: {transaction.date.isoformat()}\n"
                f"Transaction ID: {saved_id}"
            )
        return f"Transaction saved successfully!\nTransaction ID: {saved_id}"

    return last_ai_text(result) or "I couldn't generate a response. Please try again."
