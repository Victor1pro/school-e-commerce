"""
API router for user settings.

Provides endpoints for retrieving and updating persistent user settings.
Requires authentication via JWT.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_schema import UserSettingsResponse, UserSettingsUpdate
from app.service.user_settings_service import get_or_create_settings, update_settings
from app.core.auth import get_current_user


router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/", response_model=UserSettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve the authenticated user's settings.

    If the user has no settings row yet, one is automatically created.
    """
    return get_or_create_settings(db, current_user.id)


@router.patch("/", response_model=UserSettingsResponse)
def patch_settings(
    data: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Partially update the authenticated user's settings.

    Only fields provided in the request body are updated.
    """
    return update_settings(db, current_user.id, data)