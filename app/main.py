from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base, engine, get_db
from app.models import Toggle


# --------------- Lifespan ---------------

@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="PowerToggle", lifespan=lifespan)

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"
app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")


# --------------- Schemas ---------------

class ToggleCreate(BaseModel):
    name: str
    is_active: bool = False


class ToggleUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class ToggleOut(BaseModel):
    id: int
    name: str
    is_active: bool
    created_at: str | None = None

    model_config = {"from_attributes": True}


# --------------- Routes ---------------

@app.get("/")
async def root():
    return {"app": "PowerToggle", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/toggles", response_model=list[ToggleOut])
async def list_toggles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Toggle).order_by(Toggle.id))
    return result.scalars().all()


@app.post("/toggles", response_model=ToggleOut, status_code=201)
async def create_toggle(data: ToggleCreate, db: AsyncSession = Depends(get_db)):
    toggle = Toggle(name=data.name, is_active=data.is_active)
    db.add(toggle)
    await db.commit()
    await db.refresh(toggle)
    return toggle


@app.patch("/toggles/{toggle_id}", response_model=ToggleOut)
async def update_toggle(
    toggle_id: int, data: ToggleUpdate, db: AsyncSession = Depends(get_db)
):
    toggle = await db.get(Toggle, toggle_id)
    if not toggle:
        raise HTTPException(status_code=404, detail="Toggle not found")
    if data.name is not None:
        toggle.name = data.name
    if data.is_active is not None:
        toggle.is_active = data.is_active
    await db.commit()
    await db.refresh(toggle)
    return toggle


@app.delete("/toggles/{toggle_id}", status_code=204)
async def delete_toggle(toggle_id: int, db: AsyncSession = Depends(get_db)):
    toggle = await db.get(Toggle, toggle_id)
    if not toggle:
        raise HTTPException(status_code=404, detail="Toggle not found")
    await db.delete(toggle)
    await db.commit()
