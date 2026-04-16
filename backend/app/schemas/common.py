from datetime import date
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.models.entities import InputType, Priority, RoleType, TaskStatus


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    org_id: int | None = None
    email: EmailStr
    full_name: str
    role: RoleType
    password: str


class UserOut(BaseModel):
    id: int
    org_id: int | None
    email: EmailStr
    full_name: str
    role: RoleType

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    start_date: date | None = None
    end_date: date | None = None


class ProjectOut(ProjectCreate):
    id: int
    org_id: int

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    project_id: int
    workstream_id: int | None = None
    title: str
    description: str = ""
    owner_id: int | None = None
    owner_placeholder: str | None = None
    due_date: date | None = None
    priority: Priority = Priority.medium
    dependencies: list[int] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    owner_id: int | None = None
    due_date: date | None = None
    priority: Priority | None = None
    status: TaskStatus | None = None
    dependencies: list[int] | None = None


class TaskOut(BaseModel):
    id: int
    org_id: int
    project_id: int
    title: str
    description: str
    owner_id: int | None
    owner_placeholder: str | None
    due_date: date | None
    priority: Priority
    status: TaskStatus
    dependencies: list[int]

    class Config:
        from_attributes = True


class InputCreate(BaseModel):
    project_id: int
    input_type: InputType
    text: str
    filename: str | None = None


class ExtractedTask(BaseModel):
    action_item: str
    responsible_person: str | None = None
    deadline: date | None = None
    priority: Priority = Priority.medium
    dependencies: list[str] = Field(default_factory=list)
    source_reference: str


class AIExtractionResponse(BaseModel):
    tasks: list[ExtractedTask]
    summary: str


class DashboardOut(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    blocked_tasks: int
    by_owner: dict[str, int]
    risk_items: list[dict[str, Any]]
