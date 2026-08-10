from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserSignup
from app.core.security import hash_password, verify_password


def create_user(db: Session, user: UserSignup):

    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        return None

    # Create new user
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(db: Session, email: str, password: str):

    # Check if user exists
    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        return None

    # Verify password
    if not verify_password(password, user.password):
        return None

    return user