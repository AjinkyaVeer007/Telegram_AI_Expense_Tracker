from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages

from tracker.models import Transaction


class ExpenseState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    image_path: str | None
    transaction: Transaction | None
    validation_error: str | None
    saved_id: str | None


def initial_state(user_text: str, image_path: str | None = None) -> ExpenseState:
    """Build the input for app.invoke()."""
    return {
        "messages": [HumanMessage(content=user_text)],
        "image_path": image_path,
        "transaction": None,
        "validation_error": None,
        "saved_id": None,
    }
