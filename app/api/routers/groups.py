# app/api/routers/groups.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.db import crud, schemas, init, models
from typing import List


router = APIRouter(prefix="/groups", tags=["groups"])


async def _get_group_or_404(group_id: int, db: AsyncSession):
    group = await crud.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return group


async def _get_student_or_404(student_id: int, db: AsyncSession):
    student = await crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return student


@router.post("/", response_model=schemas.GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(group: schemas.GroupCreate, db: AsyncSession = Depends(init.get_db)):
    db_group = await crud.create_group(db, group)
    return {
        "id": db_group.id,
        "name": db_group.name,
        "description": db_group.description or "",
        "students": []
    }


@router.get("/{group_id}", response_model=schemas.GroupRead)
async def get_group(group_id: int, db: AsyncSession = Depends(init.get_db)):
    group = await crud.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return group


@router.get("/", response_model=List[schemas.GroupRead])
async def get_groups(db: AsyncSession = Depends(init.get_db)):
    return await crud.get_groups(db)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: int, db: AsyncSession = Depends(init.get_db)):
    success = await crud.delete_group(db, group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return None


@router.get("/{group_id}/students", response_model=List[schemas.StudentRead])
async def get_students_in_group(group_id: int, db: AsyncSession = Depends(init.get_db)):
    await _get_group_or_404(group_id, db)  # 404 если группы нет
    return await crud.get_students_in_group(db, group_id)


@router.post("/add-to-group")
async def add_to_group(data: schemas.StudentGroupOperation,
                       db: AsyncSession = Depends(init.get_db)):
    # Проверяем существование
    await _get_student_or_404(data.student_id, db)
    await _get_group_or_404(data.group_id, db)

    try:
        await crud.add_student_to_group(db, data.student_id, data.group_id)
        return {"detail": "Студент успешно добавлен в группу"}
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Студент уже состоит в этой группе"
        )


@router.post("/remove-from-group")
async def remove_from_group(data: schemas.StudentGroupOperation,
                            db: AsyncSession = Depends(init.get_db)):
    await _get_student_or_404(data.student_id, db)
    await _get_group_or_404(data.group_id, db)

    removed = await crud.remove_student_from_group(db, data.student_id, data.group_id)
    if not removed:
        raise HTTPException(
            status_code=400,
            detail="Студент не состоит в указанной группе"
        )
    return {"detail": "Студент успешно удалён из группы"}


@router.post("/move-student")
async def move_student(data: schemas.StudentMove, db: AsyncSession = Depends(init.get_db)):
    # Проверяем все сущности
    await _get_student_or_404(data.student_id, db)
    await _get_group_or_404(data.from_group_id, db)
    await _get_group_or_404(data.to_group_id, db)

    if data.from_group_id == data.to_group_id:
        raise HTTPException(status_code=400, detail="Исходная и целевая группы совпадают")

    # Проверяем, что студент действительно в from_group
    students_in_from = await crud.get_students_in_group(db, data.from_group_id)
    if data.student_id not in [s["id"] for s in students_in_from]:
        raise HTTPException(status_code=400, detail="Студент не состоит в исходной группе")

    await crud.move_student(db, data.student_id, data.from_group_id, data.to_group_id)
    return {"detail": f"Студент переведён из группы "
                      f"{data.from_group_id} в группу {data.to_group_id}"}