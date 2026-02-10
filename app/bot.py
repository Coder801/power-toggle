import logging
from pathlib import Path

from telegram import BotCommand, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.config import TELEGRAM_BOT_TOKEN

BASE_DIR = Path(__file__).resolve().parent.parent

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Почати"),
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info("Получена команда /start от %s (id=%s)", user.full_name, user.id)
    reply_keyboard = [[KeyboardButton("Почати")]]
    await update.message.reply_photo(
        photo=open(BASE_DIR / "public/images/start.png", "rb"),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )


async def on_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info("Нажата кнопка Почати от %s (id=%s)", user.full_name, user.id)
    await update.message.reply_photo(
        photo=open(BASE_DIR / "public/images/image2.png", "rb"),
    )


def create_bot() -> Application:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text(["Почати"]), on_start))
    return app


if __name__ == "__main__":
    bot = create_bot()
    bot.run_polling()
