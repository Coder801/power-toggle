import logging
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from app.config import TELEGRAM_BOT_TOKEN

BASE_DIR = Path(__file__).resolve().parent.parent

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info("Получена команда /start от %s (id=%s)", user.full_name, user.id)
    keyboard = [[InlineKeyboardButton("Start", callback_data="start")]]
    await update.message.reply_photo(
        photo=open(BASE_DIR / "public/images/start.png", "rb"),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def on_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info("Нажата кнопка Start от %s (id=%s)", query.from_user.full_name, query.from_user.id)


def create_bot() -> Application:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_start_button, pattern="^start$"))
    return app


if __name__ == "__main__":
    bot = create_bot()
    bot.run_polling()
