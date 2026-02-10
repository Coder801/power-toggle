from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="PowerToggle")

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"
app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")


@app.get("/")
async def root():
    return {"app": "PowerToggle", "status": "running"}
