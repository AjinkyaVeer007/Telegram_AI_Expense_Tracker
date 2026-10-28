"""Telegram message handlers."""

import asyncio
import logging
import tempfile
from pathlib import Path

from telegram import Message, Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from tracker.agent import app as agent_app
from tracker.agent.state import initial_state
from tracker.formatting import format_result

logger = logging.getLogger(__name__)

TELEGRAM_MAX_LENGTH = 4096
DEFAULT_RECEIPT_TEXT = "Please record the expense shown in this receipt."

START_TEXT = (
    "Welcome to your AI Expense Tracker!\n\n"
    "You can:\n"
    "• Add an expense using text\n"
    "• Send a receipt photo\n"
    "• Analyze your monthly expenses\n"
    "• Find your highest spending category\n"
    "• Get suggestions to reduce expenses\n\n"
    "Example: I spent 500 rupees on groceries."
)

HELP_TEXT = (
    "Try these commands or messages:\n\n"
    "/start - Start the bot\n"
    "/help - Show help\n\n"
    "I spent 500 on groceries\n"
    "Analyze my expenses this month\n"
    "Where am I spending the most?\n\n"
    "You can also send a receipt photo."
)


def split_message(text: str, limit: int = TELEGRAM_MAX_LENGTH) -> list[str]:
    """Split long text (e.g. an expense analysis) into Telegram-sized chunks."""
    chunks = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut <= 0:
            cut = limit
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")
    chunks.append(text)
    return chunks


async def _reply(message: Message, text: str) -> None:
    for chunk in split_message(text):
        await message.reply_text(chunk)


async def _run_agent(user_text: str, image_path: str | None = None) -> dict:
    # The LangGraph app is synchronous; run it in a thread so the bot stays responsive.
    return await asyncio.to_thread(agent_app.invoke, initial_state(user_text, image_path))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(START_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(HELP_TEXT)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return

    user_text = (message.text or message.caption or "").strip()
    await message.chat.send_action(ChatAction.TYPING)

    try:
        if message.photo:
            # The temp directory (and the receipt inside it) is deleted automatically.
            with tempfile.TemporaryDirectory() as tmp_dir:
                image_path = Path(tmp_dir) / "receipt.jpg"
                telegram_file = await context.bot.get_file(message.photo[-1].file_id)
                await telegram_file.download_to_drive(custom_path=image_path)
                result = await _run_agent(user_text or DEFAULT_RECEIPT_TEXT, str(image_path))
        elif user_text:
            result = await _run_agent(user_text)
        else:
            await message.reply_text("Please send a text message or a receipt photo.")
            return

        await _reply(message, format_result(result))

    except Exception:
        logger.exception("Error processing Telegram message")
        await message.reply_text(
            "Something went wrong while processing your request. Please try again."
        )
