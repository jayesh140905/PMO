from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import RoleType, User
from app.services.auth import has_permission


class RequestUser:
    def __init__(self, user: User):
        self.id = user.id
        self.org_id = user.org_id
        self.role = user.role
        self.permissions = user.permissions


async def get_current_user(
    x_user_email: str = Header(default="admin@vigorousone.ai"),
    db: Session = Depends(get_db),
) -> RequestUser:
    user = db.scalar(select(User).where(User.email == x_user_email))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    return RequestUser(user)


def require_permission(permission: str):
    async def checker(current_user: RequestUser = Depends(get_current_user)) -> RequestUser:
        if not has_permission(RoleType(current_user.role), permission, current_user.permissions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing {permission}")
        return current_user

    return checker
