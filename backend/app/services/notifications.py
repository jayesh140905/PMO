from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Notification, Task, TaskStatus


class NotificationService:
    def check_and_create_escalations(self, db: Session, org_id: int) -> int:
        overdue_tasks = db.scalars(
            select(Task).where(
                Task.org_id == org_id,
                Task.status != TaskStatus.completed,
                Task.due_date.is_not(None),
                Task.due_date < date.today(),
            )
        ).all()
        count = 0
        for task in overdue_tasks:
            if not task.owner_id:
                continue
            notification = Notification(
                org_id=org_id,
                user_id=task.owner_id,
                channel="email",
                subject=f"[Escalation] Overdue task: {task.title}",
                message=f"Task '{task.title}' is overdue. Please update progress immediately.",
                escalation_level=1,
                is_sent=False,
            )
            db.add(notification)
            count += 1
        db.commit()
        return count


notification_service = NotificationService()
