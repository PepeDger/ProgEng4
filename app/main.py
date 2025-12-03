# app/main.py
from fastapi import FastAPI
from app.api.routers import students, groups
from app.db.models import Base
from app.db.init import engine
import asyncio

app = FastAPI(title="Students & Groups API", version="1.0")
app.include_router(students.router)
app.include_router(groups.router)

async def create_tables():
    for i in range(10):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Таблицы успешно созданы")
            return
        except Exception as e:
            if i == 9:
                raise
            print(f"Попытка {i+1}/10 подключиться к БД... ({e})")
            await asyncio.sleep(2)

@app.on_event("startup")
async def startup():
    await create_tables()

@app.get("/")
async def root():
    return {"message": "API работает → /docs"}