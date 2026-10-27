from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.schemas.common import reject_null

# Muss zu USER_ROLES in app/models.py passen
UserRole = Literal['admin', 'platform_engineer', 'viewer']


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=255)
    role: UserRole = 'viewer'


class UserUpdate(BaseModel):
    """Alle Felder optional: nur gesetzte Felder werden geändert."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None

    @model_validator(mode='after')
    def required_fields_not_null(self):
        reject_null(self, ('name', 'email', 'role', 'is_active'))
        return self


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
