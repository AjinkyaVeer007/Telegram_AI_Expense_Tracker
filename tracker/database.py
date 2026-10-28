"""MongoDB access. One shared client (pymongo is thread-safe and pools connections)."""

from datetime import datetime
from functools import lru_cache

from pymongo import MongoClient
from pymongo.collection import Collection

from tracker.config import MONGO_COLLECTION, MONGO_DB_NAME, MONGO_URI
from tracker.models import Transaction


@lru_cache(maxsize=1)
def get_collection() -> Collection:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    collection = client[MONGO_DB_NAME][MONGO_COLLECTION]
    collection.create_index("date")  # speeds up the date-range queries
    return collection


def save_transaction(transaction: Transaction) -> str:
    """Insert a transaction and return its MongoDB id as a string."""
    document = transaction.model_dump()
    document["category"] = transaction.category.value
    result = get_collection().insert_one(document)
    return str(result.inserted_id)


def fetch_transactions_between(start: datetime, end: datetime) -> list[dict]:
    """Return transactions with start <= date < end, oldest first.

    The end date is exclusive so month boundaries never double count.
    `_id` is omitted: the agent doesn't need it and it wastes LLM tokens.
    """
    cursor = (
        get_collection()
        .find({"date": {"$gte": start, "$lt": end}}, {"_id": 0})
        .sort("date", 1)
    )

    transactions = []
    for document in cursor:
        if isinstance(document.get("date"), datetime):
            document["date"] = document["date"].isoformat()
        transactions.append(document)
    return transactions
