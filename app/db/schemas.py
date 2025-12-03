# app/db/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class StudentBase(BaseModel):
    first_name: str
    last_name: str
    age: Optional[int] = None

class StudentCreate(StudentBase):
    pass

class StudentRead(StudentBase):
    id: int
    groups: List[int] = []

    model_config = {"from_attributes": True}

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class GroupRead(GroupBase):
    id: int
    students: List[int] = []

    model_config = {"from_attributes": True}

class StudentGroupOperation(BaseModel):
    student_id: int
    group_id: int

class StudentMove(BaseModel):
    student_id: int
    from_group_id: int
    to_group_id: int