"""Build and run the Telegram application."""

import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from tracker.bot.handlers import handle_message, help_command, start
from tracker.config import require_telegram_settings, setup_logging

logger = logging.getLogger(__name__)


def build_application() -> Application:
    token, allowed_user_id = require_telegram_settings()

    # Only the allowed user's updates reach the handlers; everyone else is ignored.
    owner = filters.User(user_id=allowed_user_id)
    private = filters.ChatType.PRIVATE

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start, filters=owner))
    application.add_handler(CommandHandler("help", help_command, filters=owner))
    application.add_handler(
        MessageHandler(
            (filters.PHOTO | (filters.TEXT & ~filters.COMMAND)) & private & owner,
            handle_message,
        )
    )
    return application


def run() -> None:
    setup_logging()
    application = build_application()
    logger.info("Telegram Expense Tracker bot is starting...")
    application.run_polling()
