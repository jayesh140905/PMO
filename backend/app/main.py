from fastapi import FastAPI

from app.api.routes import router
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.entities import Organization, RoleType, User
from app.services.auth import hash_password

app = FastAPI(title="VigorousONE AI PMO API", version="0.1.0")
app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.name == "VigorousONE Demo Org").one_or_none()
        if not org:
            org = Organization(name="VigorousONE Demo Org")
            db.add(org)
            db.commit()
            db.refresh(org)
        admin = db.query(User).filter(User.email == "admin@vigorousone.ai").one_or_none()
        if not admin:
            db.add(
                User(
                    org_id=org.id,
                    email="admin@vigorousone.ai",
                    full_name="Super Admin",
                    role=RoleType.org_admin,
                    hashed_password=hash_password("admin123"),
                )
            )
            db.commit()
    finally:
        db.close()
