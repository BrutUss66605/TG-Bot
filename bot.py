#!/usr/bin/env python3
"""Telegram bot with a calculator and test payment using python-telegram-bot."""

import asyncio
import ast
import logging
import os

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ASK_EXPR = 0

# Default bot token if not set in environment
DEFAULT_BOT_TOKEN = "7611907540:AAH9_pP9YcIt32xfeODBhYODbTernSNnRLA"

# CONSTANTS
WELCOME_TEXT = (
    "\U0001F44B Привет! Я бот на базе ИИ, который помогает прогнозировать вероятность победы.\n\n"
    "Вот что я умею:\n"
    "• \U0001F522 Калькулятор — быстро считаю выражения.\n"
    "• \U0001F4B3 Оплата — демонстрация тестового платежа.\n\n"
    "Чтобы начать, нажми кнопку ниже или отправь /help."
)

MAIN_KB = ReplyKeyboardMarkup(
    [["🔢 Калькулятор", "💳 Оплата"]],
    resize_keyboard=True,
    one_time_keyboard=False,
)


def load_tokens() -> tuple[str, str]:
    """Load required tokens from environment."""
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN") or DEFAULT_BOT_TOKEN
    provider_token = os.getenv("PROVIDER_TOKEN")
    if not bot_token or not provider_token:
        logger.error("BOT_TOKEN or PROVIDER_TOKEN is missing")
        raise SystemExit(1)
    return bot_token, provider_token


def safe_eval(expr: str) -> float:
    """Safely evaluate a basic math expression."""
    node = ast.parse(expr, mode="eval")
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Num,
        ast.Load,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.Constant,
    )
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            raise ValueError
        if not isinstance(n, allowed):
            raise ValueError
    return eval(compile(node, "<expr>", "eval"), {"__builtins__": {}}, {})


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.get_me()
    logger.info("Пользователь %s вызвал /start", update.effective_user.id)
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=MAIN_KB,
        parse_mode="Markdown",
    )


async def calc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите выражение:")
    return ASK_EXPR


async def evaluate_expression(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        result = safe_eval(update.message.text)
        await update.message.reply_text(str(result))
    except Exception:
        await update.message.reply_text("Ошибка выражения")
    return ConversationHandler.END


async def pay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prices = [LabeledPrice(label="Пополнение счёта", amount=10000)]
    await update.message.reply_invoice(
        title="Пополнение счёта",
        description="Тестовый платёж",
        payload="test_payload",
        provider_token=context.bot_data.get("PROVIDER_TOKEN"),
        currency="RUB",
        prices=prices,
    )


async def precheckout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Платёж успешно прошёл!")


async def main() -> None:
    bot_token, provider_token = load_tokens()

    application = Application.builder().token(bot_token).build()
    application.bot_data["PROVIDER_TOKEN"] = provider_token

    me = await application.bot.get_me()
    logger.info("Bot %s connected", me.first_name)

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("calc", calc_cmd),
            MessageHandler(filters.Regex("^🔢 Калькулятор$"), calc_cmd),
        ],
        states={ASK_EXPR: [MessageHandler(filters.TEXT & ~filters.COMMAND, evaluate_expression)]},
        fallbacks=[],
    )

    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(conv)
    application.add_handler(CommandHandler("pay", pay_cmd))
    application.add_handler(MessageHandler(filters.Regex("^💳 Оплата$"), pay_cmd))
    application.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

    logger.info("Bot started")
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
