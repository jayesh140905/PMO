from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import RequestUser, get_current_user, require_permission
from app.db.session import get_db
from app.models.entities import AIOutput, InputType, Organization, Project, SourceInput, Task, TaskAuditLog, TaskStatus, User
from app.schemas.common import DashboardOut, InputCreate, ProjectCreate, ProjectOut, TaskCreate, TaskOut, TaskUpdate, UserCreate, UserOut
from app.services.ai import ai_engine, extraction_prompt_template
from app.services.auth import create_access_token, hash_password, verify_password
from app.services.dashboard import dashboard_service
from app.services.notifications import notification_service

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "vigorousone-ai-pmo"}


@router.post("/auth/register", response_model=UserOut)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.email == payload.email))
    if exists:
        raise HTTPException(status_code=409, detail="Email already exists")
    user = User(
        org_id=payload.org_id,
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/token")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=user.email, role=user.role.value, org_id=user.org_id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/organizations")
def create_org(name: str, db: Session = Depends(get_db), _: RequestUser = Depends(require_permission("org:manage"))):
    org = Organization(name=name)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.post("/projects", response_model=ProjectOut)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: RequestUser = Depends(require_permission("project:manage")),
):
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="User must belong to organization")
    project = Project(org_id=current_user.org_id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: RequestUser = Depends(require_permission("dashboard:view")),
):
    return db.scalars(select(Project).where(Project.org_id == current_user.org_id)).all()


@router.post("/tasks", response_model=TaskOut)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: RequestUser = Depends(require_permission("task:manage")),
):
    task = Task(org_id=current_user.org_id, created_by=current_user.id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    db.add(TaskAuditLog(task_id=task.id, actor_id=current_user.id, action="created", after_state=payload.model_dump()))
    db.commit()
    return task


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: RequestUser = Depends(get_current_user),
):
    task = db.scalar(select(Task).where(Task.id == task_id, Task.org_id == current_user.org_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_id == current_user.id:
        pass
    elif current_user.role in ["super_admin", "org_admin", "project_manager"]:
        pass
    else:
        raise HTTPException(status_code=403, detail="Cannot update this task")

    before = {
        "title": task.title,
        "status": task.status.value,
        "priority": task.priority.value,
        "owner_id": task.owner_id,
    }
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)

    if task.due_date and task.due_date < date.today() and task.status != TaskStatus.completed:
        task.status = TaskStatus.overdue

    db.commit()
    db.refresh(task)

    db.add(TaskAuditLog(task_id=task.id, actor_id=current_user.id, action="updated", before_state=before, after_state=updates))
    db.commit()
    return task


@router.post("/inputs/upload")
def upload_input(
    payload: InputCreate,
    db: Session = Depends(get_db),
    current_user: RequestUser = Depends(require_permission("ai:use")),
):
    source = SourceInput(
        org_id=current_user.org_id,
        project_id=payload.project_id,
        input_type=InputType(payload.input_type),
        filename=payload.filename,
        raw_text=payload.text,
        transcript=payload.text if payload.input_type == InputType.meeting else None,
        created_by=current_user.id,
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    extraction = ai_engine.extract_tasks(payload.text, f"{payload.input_type}:{source.id}")
    created = []
    for item in extraction.tasks:
        task = Task(
            org_id=current_user.org_id,
            project_id=payload.project_id,
            title=item.action_item,
            description=f"Auto-extracted from source #{source.id}",
            owner_placeholder=item.responsible_person,
            due_date=item.deadline,
            priority=item.priority,
            dependencies=item.dependencies,
            source_input_id=source.id,
            created_by=current_user.id,
        )
        db.add(task)
        created.append(task)

    mom = ai_engine.generate_mom(payload.text)
    db.add(
        AIOutput(
            org_id=current_user.org_id,
            project_id=payload.project_id,
            source_input_id=source.id,
            output_type="mom",
            content=mom,
            metadata_json={"prompt": extraction_prompt_template(), "summary": extraction.summary},
            created_by=current_user.id,
        )
    )
    db.commit()

    return {
        "source_input_id": source.id,
        "extracted_tasks": len(created),
        "summary": extraction.summary,
        "mom_preview": mom,
    }


@router.post("/monitoring/run")
def run_monitoring(
    db: Session = Depends(get_db),
    current_user: RequestUser = Depends(require_permission("task:manage")),
):
    created_notifications = notification_service.check_and_create_escalations(db, current_user.org_id)
    return {"created_notifications": created_notifications}


@router.get("/dashboards/control-tower", response_model=DashboardOut)
def control_tower_dashboard(
    db: Session = Depends(get_db),
    current_user: RequestUser = Depends(require_permission("dashboard:view")),
):
    return dashboard_service.get_project_control_tower(db, current_user.org_id)
