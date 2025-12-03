# app/db/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
from .models import Student, Group, student_group


async def create_student(db: AsyncSession, data):
    student = Student(**data.model_dump())
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


async def get_student(db: AsyncSession, student_id: int):
    student = await db.get(Student, student_id)
    if not student:
        return None
    result = await db.execute(select(student_group.c.group_id)
                              .where(student_group.c.student_id == student_id))
    groups = [row[0] for row in result.all()]
    return {
        "id": student.id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "age": student.age,
        "groups": groups
    }


async def get_students(db: AsyncSession):
    result = await db.execute(select(Student))
    students = []
    for s in result.scalars():
        res = await db.execute(select(student_group.c.group_id)
                               .where(student_group.c.student_id == s.id))
        groups = [row[0] for row in res.all()]
        students.append({
            "id": s.id,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "age": s.age,
            "groups": groups
        })
    return students


async def delete_student(db: AsyncSession, student_id: int):
    student = await db.get(Student, student_id)
    if student:
        await db.delete(student)
        await db.commit()
        return True
    return False


async def create_group(db: AsyncSession, data):
    group = Group(**data.model_dump())
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


async def get_group(db: AsyncSession, group_id: int):
    group = await db.get(Group, group_id)
    if not group:
        return None
    result = await db.execute(select(student_group.c.student_id)
                              .where(student_group.c.group_id == group_id))
    students = [row[0] for row in result.all()]
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "students": students
    }


async def get_groups(db: AsyncSession):
    result = await db.execute(select(Group))
    groups = []
    for g in result.scalars():
        res = await db.execute(select(student_group.c.student_id)
                               .where(student_group.c.group_id == g.id))
        students = [row[0] for row in res.all()]
        groups.append({
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "students": students
        })
    return groups


async def delete_group(db: AsyncSession, group_id: int):
    group = await db.get(Group, group_id)
    if group:
        await db.delete(group)
        await db.commit()
        return True
    return False


async def get_students_in_group(db: AsyncSession, group_id: int):
    result = await db.execute(
        select(Student.id, Student.first_name, Student.last_name, Student.age)
        .join(student_group)
        .where(student_group.c.group_id == group_id)
    )
    students = []
    for row in result.all():
        student_id = row[0]
        group_res = await db.execute(select(student_group.c.group_id)
                                     .where(student_group.c.student_id == student_id))
        groups = [g[0] for g in group_res.all()]
        students.append({
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "age": row[3],
            "groups": groups
        })
    return students


async def add_student_to_group(db: AsyncSession, student_id: int, group_id: int):
    await db.execute(insert(student_group).values(student_id=student_id, group_id=group_id))
    await db.commit()


async def remove_student_from_group(db: AsyncSession, student_id: int, group_id: int):
    await db.execute(delete(student_group).where(
        student_group.c.student_id == student_id,
        student_group.c.group_id == group_id
    ))
    await db.commit()


async def move_student(db: AsyncSession, student_id: int, from_group_id: int, to_group_id: int):
    await remove_student_from_group(db, student_id, from_group_id)
    await add_student_to_group(db, student_id, to_group_id)