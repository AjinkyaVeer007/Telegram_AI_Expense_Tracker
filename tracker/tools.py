"""LangChain tools the agent can call.

Docstrings are sent to the LLM as tool descriptions, so edit them with care.
"""

import base64
import logging
import os
from datetime import datetime

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from tracker.database import fetch_transactions_between
from tracker.llm import structured_llm
from tracker.models import Transaction, TransactionCategory
from tracker.prompts import IMAGE_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


def _error(exc: Exception | str) -> dict:
    return {"type": "error", "error": str(exc)}


def _image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image:
        return base64.b64encode(image.read()).decode("utf-8")


@tool
def create_transaction(
    amount: int,
    purpose: str,
    category: TransactionCategory,
    date: str,
) -> dict:
    """
    Create a transaction from information provided
    by the user in natural language.

    category must be one of the TransactionCategory values.

    If the user does not provide a date,
    use the current date/time supplied by the agent.

    Example:
    User: I gave 2000 rupees to my friend Rupesh.
    Use: amount = 2000, purpose = Given money to friend Rupesh, category = help
    """
    try:
        transaction = Transaction(
            amount=amount,
            purpose=purpose,
            category=category,
            date=datetime.fromisoformat(date),
        )
        return {"type": "transaction", "data": transaction.model_dump(mode="json")}
    except Exception as exc:
        return _error(exc)


@tool
def extract_transaction_from_image(image_path: str) -> dict:
    """
    Extract transaction information from an
    expense receipt or transaction slip image.

    Returns: amount, date, purpose, category.
    """
    try:
        if not image_path:
            return _error("No image path provided.")
        if not os.path.exists(image_path):
            return _error(f"Image not found: {image_path}")

        message = HumanMessage(
            content=[
                {"type": "text", "text": IMAGE_EXTRACTION_PROMPT},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{_image_to_base64(image_path)}"
                    },
                },
            ]
        )
        response = structured_llm.invoke([message])
        return {"type": "transaction", "data": response.model_dump(mode="json")}
    except Exception as exc:
        logger.exception("Receipt extraction failed")
        return _error(exc)


@tool
def fetch_transactions(start_date: str, end_date: str) -> dict:
    """
    Fetch transactions from MongoDB.

    start_date and end_date must be ISO datetime strings.
    start_date is inclusive, end_date is exclusive.

    Example:
    start_date: 2026-10-01T00:00:00+00:00
    end_date:   2026-11-01T00:00:00+00:00

    Use this tool when the user asks for:
    - total expenses
    - monthly expenses
    - spending analysis
    - category-wise expenses
    - highest expenses
    - unnecessary expenses
    - spending patterns
    - expense suggestions
    - expense reports
    """
    try:
        transactions = fetch_transactions_between(
            datetime.fromisoformat(start_date),
            datetime.fromisoformat(end_date),
        )
        return {
            "type": "transactions",
            "count": len(transactions),
            "transactions": transactions,
        }
    except Exception as exc:
        logger.exception("Fetching transactions failed")
        return _error(exc)


ALL_TOOLS = [create_transaction, extract_transaction_from_image, fetch_transactions]

# Tools whose result is a Transaction that must be validated and saved.
TRANSACTION_TOOL_NAMES = {"create_transaction", "extract_transaction_from_image"}
