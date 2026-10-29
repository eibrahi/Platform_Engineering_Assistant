from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import reject_null

# Muss zu ENVIRONMENTS / PLATFORM_STATUSES in app/models.py passen
Environment = Literal['dev', 'test', 'prod']
PlatformStatus = Literal['healthy', 'degraded', 'down', 'unknown']


class PlatformBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    environment: Environment
    cloud_provider: str = Field(default='azure', max_length=50)
    azure_subscription_id: str | None = Field(default=None, max_length=64)
    azure_region: str | None = Field(default=None, max_length=50)
    databricks_workspace_url: str | None = Field(default=None, max_length=255)
    status: PlatformStatus = 'unknown'


class PlatformCreate(PlatformBase):
    pass


class PlatformUpdate(BaseModel):
    """Alle Felder optional: nur gesetzte Felder werden geändert."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    environment: Environment | None = None
    cloud_provider: str | None = Field(default=None, max_length=50)
    azure_subscription_id: str | None = Field(default=None, max_length=64)
    azure_region: str | None = Field(default=None, max_length=50)
    databricks_workspace_url: str | None = Field(default=None, max_length=255)
    status: PlatformStatus | None = None

    @model_validator(mode='after')
    def required_fields_not_null(self):
        reject_null(self, ('name', 'environment', 'cloud_provider', 'status'))
        return self


class PlatformRead(PlatformBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
