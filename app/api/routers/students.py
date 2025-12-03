# app/api/routers/students.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud, schemas, init
from typing import List

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/", response_model=schemas.StudentRead, status_code=201)
async def create_student(student: schemas.StudentCreate, db: AsyncSession = Depends(init.get_db)):
    db_student = await crud.create_student(db, student)
    return {
        "id": db_student.id,
        "first_name": db_student.first_name,
        "last_name": db_student.last_name,
        "age": db_student.age,
        "groups": []
    }

@router.get("/{student_id}", response_model=schemas.StudentRead)
async def get_student(student_id: int, db: AsyncSession = Depends(init.get_db)):
    student = await crud.get_student(db, student_id)
    if not student:
        raise HTTPException(404, "Студент не найден")
    return student

@router.get("/", response_model=List[schemas.StudentRead])
async def get_students(db: AsyncSession = Depends(init.get_db)):
    return await crud.get_students(db)

@router.delete("/{student_id}", status_code=204)
async def delete_student(student_id: int, db: AsyncSession = Depends(init.get_db)):
    if not await crud.delete_student(db, student_id):
        raise HTTPException(404, "Студент не найден")
