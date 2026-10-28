import logging
import os

from dotenv import load_dotenv

load_dotenv()

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "telegram-rag")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "transactions")

# LLM
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Telegram (only needed when running the bot, not the CLI)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")


def require_telegram_settings() -> tuple[str, int]:
    """Return (bot_token, allowed_user_id) or raise if missing."""
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing from .env")
    if not TELEGRAM_ALLOWED_USER_ID:
        raise RuntimeError("TELEGRAM_ALLOWED_USER_ID is missing from .env")
    return TELEGRAM_BOT_TOKEN, int(TELEGRAM_ALLOWED_USER_ID)


def setup_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    # httpx logs full request URLs at INFO, which include the Telegram bot token.
    logging.getLogger("httpx").setLevel(logging.WARNING)
