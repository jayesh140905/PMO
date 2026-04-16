from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import Task, TaskStatus, User
from app.schemas.common import DashboardOut


class DashboardService:
    def get_project_control_tower(self, db: Session, org_id: int) -> DashboardOut:
        total = db.scalar(select(func.count()).where(Task.org_id == org_id)) or 0
        completed = (
            db.scalar(select(func.count()).where(Task.org_id == org_id, Task.status == TaskStatus.completed)) or 0
        )
        overdue = db.scalar(select(func.count()).where(Task.org_id == org_id, Task.status == TaskStatus.overdue)) or 0
        blocked = db.scalar(select(func.count()).where(Task.org_id == org_id, Task.status == TaskStatus.blocked)) or 0
        pending = total - completed

        owner_rows = db.execute(
            select(User.full_name, func.count(Task.id))
            .join(Task, Task.owner_id == User.id)
            .where(Task.org_id == org_id)
            .group_by(User.full_name)
        ).all()
        by_owner = {name: count for name, count in owner_rows}

        risk_tasks = db.scalars(
            select(Task).where(Task.org_id == org_id, Task.status.in_([TaskStatus.overdue, TaskStatus.blocked]))
        ).all()
        risk_items = [
            {"task_id": task.id, "title": task.title, "status": task.status.value, "priority": task.priority.value}
            for task in risk_tasks
        ]

        return DashboardOut(
            total_tasks=total,
            completed_tasks=completed,
            pending_tasks=pending,
            overdue_tasks=overdue,
            blocked_tasks=blocked,
            by_owner=by_owner,
            risk_items=risk_items,
        )


dashboard_service = DashboardService()
