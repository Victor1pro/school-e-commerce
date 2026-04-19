"""
Service layer for user settings.

Contains business logic for retrieving and updating user settings.
Abstracts database operations away from the router.
"""

from sqlalchemy.orm import Session
from app.models.user_model import UserSettings
from app.schemas.user_schema import UserSettingsUpdate


def get_or_create_settings(db: Session, user_id: int) -> UserSettings:
    """
    Retrieve the user's settings row, creating it if it does not exist.

    Args:
        db (Session): Active database session.
        user_id (int): ID of the authenticated user.

    Returns:
        UserSettings: The user's settings record.
    """
    settings = db.get(UserSettings, user_id)

    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


def update_settings(db: Session, user_id: int, data: UserSettingsUpdate) -> UserSettings:
    """
    Update the user's settings with the provided fields.

    Only fields explicitly sent by the client are updated.

    Args:
        db (Session): Active database session.
        user_id (int): ID of the authenticated user.
        data (UserSettingsUpdate): Partial update payload.

    Returns:
        UserSettings: Updated settings record.
    """
    settings = get_or_create_settings(db, user_id)

    for field, value in data.dict(exclude_unset=True).items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)
    return settings