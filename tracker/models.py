"""Domain models: transaction categories and the Transaction schema."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TransactionCategory(str, Enum):
    EMI = "emi"
    RENT = "rent"
    FOOD = "food"
    GROCERIES = "groceries"
    SHOPPING = "shopping"
    BILLS = "bills"
    HEALTH = "health"
    ENTERTAINMENT = "entertainment"
    INVESTMENT = "investment"
    EDUCATION = "education"
    TRAVEL = "travel"
    HELP = "help"
    BORROW = "borrow"
    OTHER = "other"


# Single source of truth for prompts.
CATEGORY_TEXT = ", ".join(category.value for category in TransactionCategory)


class Transaction(BaseModel):
    amount: int = Field(description="Transaction amount in Indian rupees")
    date: datetime = Field(description="Transaction date and time")
    purpose: str = Field(description="Purpose of the transaction")
    category: TransactionCategory = Field(
        description="Most appropriate transaction category"
    )
