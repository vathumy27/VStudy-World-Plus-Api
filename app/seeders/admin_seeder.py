"""Seed the default Admin account."""

from app.extensions import db
from app.models.user import User

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"
ADMIN_NAME = "System Admin"
ADMIN_ROLE = "Admin"


def seed_admin(force_password: bool = False) -> dict:
    """
    Create or update the default admin user.

    - Creates admin@gmail.com / admin123 if missing.
    - Ensures role is Admin.
    - Optionally resets password when force_password=True.
    """
    email = ADMIN_EMAIL.strip().lower()
    user = User.query.filter_by(email=email).first()

    if user:
        changed = False
        if user.role != ADMIN_ROLE:
            user.role = ADMIN_ROLE
            changed = True
        if force_password:
            user.set_password(ADMIN_PASSWORD)
            changed = True
        if not user.full_name:
            user.full_name = ADMIN_NAME
            changed = True
        if changed:
            db.session.commit()
            return {
                "action": "updated",
                "email": user.email,
                "role": user.role,
                "id": user.id,
            }
        return {
            "action": "exists",
            "email": user.email,
            "role": user.role,
            "id": user.id,
        }

    user = User(
        full_name=ADMIN_NAME,
        email=email,
        role=ADMIN_ROLE,
        school="VStudy World Plus",
        grade=None,
    )
    user.set_password(ADMIN_PASSWORD)
    db.session.add(user)
    db.session.commit()
    return {
        "action": "created",
        "email": user.email,
        "role": user.role,
        "id": user.id,
    }
