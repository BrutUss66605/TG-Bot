#!/usr/bin/env python3
"""Minimal Telegram bot skeleton.

1. Create a file named `.env` next to this script with a single line:
   BOT_TOKEN=<your-token-here>

2. Install dependencies:
   pip install -r requirements.txt

3. Run the bot:
   python bot.py
"""

import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Load token from .env file
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start command handler"""
    await update.message.reply_text(
        "Привет! Я минимальный бот, созданный через Codex.\n"
        "Напиши /help, чтобы узнать, что я умею."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help command handler"""
    await update.message.reply_text(
        "/start – приветствие\n"
        "/help – эта справка\n"
        "Напиши что‑нибудь, и я повторю это обратно!"  # echo feature
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo handler for any text message that is not a command"""
    await update.message.reply_text(update.message.text)


async def main() -> None:
    """Main entry point"""
    if not TOKEN:
        logger.error("BOT_TOKEN не найден. Проверь .env файл.")
        return

    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
