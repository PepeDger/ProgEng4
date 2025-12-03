# app/api/routers/groups.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud, schemas, init
from typing import List

router = APIRouter(prefix="/groups", tags=["groups"])

@router.post("/", response_model=schemas.GroupRead, status_code=201)
async def create_group(group: schemas.GroupCreate, db: AsyncSession = Depends(init.get_db)):
    db_group = await crud.create_group(db, group)
    return {
        "id": db_group.id,
        "name": db_group.name,
        "description": db_group.description,
        "students": []
    }

@router.get("/{group_id}", response_model=schemas.GroupRead)
async def get_group(group_id: int, db: AsyncSession = Depends(init.get_db)):
    group = await crud.get_group(db, group_id)
    if not group:
        raise HTTPException(404, "Группа не найдена")
    return group

@router.get("/", response_model=List[schemas.GroupRead])
async def get_groups(db: AsyncSession = Depends(init.get_db)):
    return await crud.get_groups(db)

@router.delete("/{group_id}", status_code=204)
async def delete_group(group_id: int, db: AsyncSession = Depends(init.get_db)):
    if not await crud.delete_group(db, group_id):
        raise HTTPException(404)

@router.get("/{group_id}/students", response_model=List[schemas.StudentRead])
async def get_students_in_group(group_id: int, db: AsyncSession = Depends(init.get_db)):
    return await crud.get_students_in_group(db, group_id)

@router.post("/add-to-group")
async def add_to_group(data: schemas.StudentGroupOperation, db: AsyncSession = Depends(init.get_db)):
    await crud.add_student_to_group(db, data.student_id, data.group_id)
    return {"detail": "Добавлен"}

@router.post("/remove-from-group")
async def remove_from_group(data: schemas.StudentGroupOperation, db: AsyncSession = Depends(init.get_db)):
    await crud.remove_student_from_group(db, data.student_id, data.group_id)
    return {"detail": "Удалён"}

@router.post("/move-student")
async def move_student(data: schemas.StudentMove, db: AsyncSession = Depends(init.get_db)):
    await crud.move_student(db, data.student_id, data.from_group_id, data.to_group_id)
    return {"detail": "Переведён"}