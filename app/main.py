from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.bot import create_bot
from app.config import TELEGRAM_BOT_TOKEN


@asynccontextmanager
async def lifespan(_app: FastAPI):
    bot = create_bot()
    await bot.initialize()
    await bot.updater.start_polling()
    await bot.start()
    yield
    await bot.updater.stop()
    await bot.stop()
    await bot.shutdown()


app = FastAPI(title="PowerToggle", lifespan=lifespan)

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"
app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")


@app.get("/")
async def root():
    return {"app": "PowerToggle", "status": "running", "version": "0.1.0", "TOKEN": TELEGRAM_BOT_TOKEN.split(":")[0] + ":***"}
