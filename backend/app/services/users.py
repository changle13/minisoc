from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models import User


def create_user(db: Session, username: str, password: str, role: str) -> User:
    user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed_admin(db: Session) -> None:
    existing = db.scalar(select(User).where(User.username == settings.admin_username))
    if existing is not None:
        return
    create_user(db, settings.admin_username, settings.admin_password, role="admin")
