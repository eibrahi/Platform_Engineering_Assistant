from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import reject_null

# Muss zu INCIDENT_SEVERITIES / INCIDENT_STATUSES in app/models.py passen
IncidentSeverity = Literal['low', 'medium', 'high', 'critical']
IncidentStatus = Literal['open', 'investigating', 'resolved']


class IncidentCreate(BaseModel):
    """Status ist beim Anlegen immer 'open' und wird deshalb nicht angenommen."""

    platform_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    severity: IncidentSeverity = 'medium'


class IncidentUpdate(BaseModel):
    """platform_id und resolved_at sind bewusst nicht änderbar."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    severity: IncidentSeverity | None = None
    status: IncidentStatus | None = None
    root_cause: str | None = None

    @model_validator(mode='after')
    def required_fields_not_null(self):
        reject_null(self, ('title', 'severity', 'status'))
        return self


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    platform_id: int
    title: str
    description: str | None
    severity: IncidentSeverity
    status: IncidentStatus
    root_cause: str | None
    created_at: datetime
    resolved_at: datetime | None
