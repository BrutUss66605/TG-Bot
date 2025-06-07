#!/usr/bin/env python3
"""Simple Telegram bot with a hidden calculator.

1. Create a file named `.env` next to this script with the lines::

       BOT_TOKEN=<your-token-here>
       DEVELOPER_ID=<your-telegram-user-id>

2. Install dependencies::

       pip install -r requirements.txt

3. Run the bot::

       python bot.py
"""

import asyncio
import json
import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
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

# Load token and developer ID from .env file
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
DEVELOPER_ID = int(os.getenv("DEVELOPER_ID", "0"))
HISTORY_FILE = "history.json"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    keyboard = [
        [
            InlineKeyboardButton("Оплата", callback_data="payment"),
            InlineKeyboardButton("Тарифы", callback_data="tariffs"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Этот бот может вычислять результаты и сохранять их.",
        reply_markup=reply_markup,
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text(
        "/start – приветствие\n"
        "/help – эта справка\n"
        "/calc <числа> – скрытый калькулятор\n"
        "/payment – как оплатить\n"
        "/tariffs – доступные тарифы\n"
        "/history – история (только для разработчика)"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo handler for any text message that is not a command"""
    await update.message.reply_text(update.message.text)


def calculate_formula(numbers: list[float]) -> float:
    """Hidden calculation formula. Replace with your own logic."""
    return sum(numbers)


def load_history() -> list:
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_history(entry: dict) -> None:
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hidden calculator command."""
    if not context.args:
        await update.message.reply_text("Использование: /calc число1 число2 ...")
        return
    try:
        numbers = [float(arg.replace(",", ".")) for arg in context.args]
    except ValueError:
        await update.message.reply_text("Нужно передать числа через пробел.")
        return

    result = calculate_formula(numbers)
    await update.message.reply_text(f"Результат: {result}")
    save_history({"user": update.effective_user.id, "numbers": numbers, "result": result})


async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send payment information."""
    await update.message.reply_text("Для оплаты свяжитесь с разработчиком.")


async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send tariffs information."""
    await update.message.reply_text("Доступные тарифы: базовый и про.")


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show history to developer only."""
    if update.effective_user.id != DEVELOPER_ID:
        await update.message.reply_text("История доступна только разработчику.")
        return
    data = load_history()
    if not data:
        await update.message.reply_text("История пуста.")
        return
    text = json.dumps(data, ensure_ascii=False, indent=2)
    await update.message.reply_text(f"<code>{text}</code>", parse_mode="HTML")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button callbacks."""
    query = update.callback_query
    await query.answer()
    if query.data == "payment":
        await payment(update, context)
    elif query.data == "tariffs":
        await tariffs(update, context)


async def main() -> None:
    """Main entry point"""
    if not TOKEN:
        logger.error("BOT_TOKEN не найден. Проверь .env файл.")
        return

    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("calc", calc))
    application.add_handler(CommandHandler("payment", payment))
    application.add_handler(CommandHandler("tariffs", tariffs))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
