import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.bot import create_bot
from app.config import TELEGRAM_BOT_TOKEN
from app.devices import get_power_status, monitoring_chats, pop_stale_devices, register_ping, subscribers

logger = logging.getLogger(__name__)


class PingData(BaseModel):
    deviceId: str
    server: str = ""
    status: str = ""
    httpCode: int = 0
    uptimeMs: int = 0


async def notify_subscribers(bot, text: str):
    for chat_id in list(subscribers):
        try:
            await bot.send_message(chat_id=chat_id, text=text)
        except Exception:
            logger.warning("Не удалось отправить сообщение в chat_id=%s", chat_id)


async def stale_checker(bot):
    while True:
        await asyncio.sleep(30)
        stale = pop_stale_devices()
        for d in stale:
            text = f"🔴 Пристрій {d.device_id} офлайн\nНе відповідає >5 хв"
            await notify_subscribers(bot, text)


async def status_reporter(bot):
    while True:
        await asyncio.sleep(300)  # 5 минут
        if not monitoring_chats:
            continue
        text = get_power_status()
        for chat_id in list(monitoring_chats):
            try:
                await bot.send_message(chat_id=chat_id, text=text)
            except Exception:
                logger.warning("Не удалось отправить статус в chat_id=%s", chat_id)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    bot_app = create_bot()
    await bot_app.initialize()
    await bot_app.updater.start_polling()
    await bot_app.start()

    _app.state.bot = bot_app.bot
    stale_task = asyncio.create_task(stale_checker(bot_app.bot))
    status_task = asyncio.create_task(status_reporter(bot_app.bot))

    yield

    stale_task.cancel()
    status_task.cancel()
    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()


app = FastAPI(title="PowerToggle", lifespan=lifespan)

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"
app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")


@app.get("/")
async def root():
    return {"app": "PowerToggle", "status": "running", "version": "0.1.0", "TOKEN": TELEGRAM_BOT_TOKEN.split(":")[0] + ":***"}


@app.post("/ping")
async def ping(data: PingData):
    is_new = register_ping(data.model_dump())
    if is_new:
        text = f"🟢 Пристрій {data.deviceId} онлайн\nServer: {data.server}"
        await notify_subscribers(app.state.bot, text)
    return {"ok": True, "new": is_new}
