"""
User, Settings and Address Pydantic Schemas.

This module defines all request and response schemas related to:
- User registration
- User login
- User profile updates
- Address creation and updates
- Authentication responses
- User Settimgs: Data exchange between API & client

All schemas use Pydantic models for validation and FastAPI response serialization.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, UUID4
from datetime import datetime
from typing import Optional, List


# =========================================================
# Base User Schema
# =========================================================
class UserBase(BaseModel):
    """
    Base schema shared by multiple user-related models.

    Includes only the core user-identifying fields that are safe
    to expose or reuse across create, update, and response schemas.
    """
    email: EmailStr
    name: str


# =========================================================
# User Create Schema
# =========================================================
class UserCreate(UserBase):
    """
    Schema used when registering a new user.

    Inherits:
        - email
        - name

    Adds:
        - password: validated with length constraints
    """
    password: str = Field(
        min_length=12,
        max_length=16,
        description="Password must be between 12 and 16 characters."
    )


# =========================================================
# User Login Schema
# =========================================================
class UserLogin(BaseModel):
    """
    Schema for user login requests.

    Contains only the credentials required to authenticate.
    """
    email: EmailStr
    password: str


# =========================================================
# Address Schemas
# =========================================================
class AddressBase(BaseModel):
    """
    Base schema for address fields.

    Shared by create, update, and response schemas.
    """
    line1: str
    line2: Optional[str] = None
    city: str
    postal_code: str
    country: str
    phone: Optional[str] = None


class AddressCreate(AddressBase):
    """
    Schema for creating a new address.

    Inherits all fields from AddressBase.
    """
    pass


class AddressUpdate(BaseModel):
    """
    Schema for updating an existing address.

    All fields are optional to allow partial updates.
    """
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None


class AddressResponse(AddressBase):
    """
    Response schema for returning address information.

    Includes:
        - id: unique identifier
        - created_at: timestamp of creation
        - updated_at: timestamp of last update
    """
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Allows ORM objects (SQLAlchemy) to be converted automatically
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# User Response Schema
# =========================================================
class UserResponse(UserBase):
    """
    Response schema for returning full user details.

    Extends UserBase with:
        - id: unique user identifier
        - role: user role (e.g., admin, customer)
        - is_active: account status
        - created_at / updated_at timestamps
        - addresses: list of associated AddressResponse objects
    """
    id: UUID4
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Nested list of addresses belonging to the user
    addresses: Optional[List[AddressResponse]] = None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# User Update Schema
# =========================================================
class UserUpdate(BaseModel):
    """
    Schema for updating user profile information.

    All fields are optional to support partial updates.
    """
    name: Optional[str] = None
    password: Optional[str] = Field(
        default=None,
        min_length=12,
        max_length=16,
        description="Password must be between 12 and 16 characters."
    )


# =========================================================
# Login Response Schema
# =========================================================
class LoginResponse(BaseModel):
    """
    Response schema returned after successful authentication.

    Includes:
        - access_token: short-lived JWT
        - refresh_token: long-lived token for renewing sessions
        - token_type: typically 'bearer'
        - user: full UserResponse object
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


class UserSettingsBase(BaseModel):
    """
    Base schema containing all user settings fields.

    These fields represent persistent, account-level preferences
    that should sync across devices and sessions.
    """

    email_notifications: Optional[bool] = True
    order_updates: Optional[bool] = True
    marketing_emails: Optional[bool] = False
    two_factor_enabled: Optional[bool] = False
    privacy_tracking: Optional[bool] = False

    # Optional UI preferences synced across devices
    preferred_theme: Optional[str] = "system"  # "light", "dark", "system"
    text_size: Optional[int] = 100  # percentage scaling


class UserSettingsUpdate(UserSettingsBase):
    """
    Schema used for PATCH requests.

    All fields are optional, allowing partial updates.
    """
    pass


class UserSettingsResponse(UserSettingsBase):
    """
    Response schema returned to the client.

    Enables ORM mode so SQLAlchemy models can be returned directly.
    """

    model_config = ConfigDict(
        from_attributes = True
    )