from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.models.entities import RoleType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ROLE_PERMISSIONS = {
    RoleType.super_admin: {"*"},
    RoleType.org_admin: {
        "org:manage",
        "project:manage",
        "task:manage",
        "dashboard:view",
        "user:manage",
        "ai:use",
    },
    RoleType.project_manager: {"project:manage", "task:manage", "dashboard:view", "ai:use"},
    RoleType.team_member: {"task:update_own", "dashboard:view", "ai:use"},
    RoleType.external_stakeholder: {"task:view_assigned", "task:comment", "dashboard:view"},
    RoleType.viewer: {"dashboard:view", "task:view"},
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(*, subject: str, role: str, org_id: int | None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.token_expiry_minutes)
    payload = {"sub": subject, "role": role, "org_id": org_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def has_permission(role: RoleType, permission: str, custom_permissions: dict | None = None) -> bool:
    custom = set((custom_permissions or {}).get("allow", []))
    denied = set((custom_permissions or {}).get("deny", []))
    role_perms = ROLE_PERMISSIONS.get(role, set())
    if "*" in role_perms:
        return permission not in denied
    return (permission in role_perms or permission in custom) and permission not in denied
