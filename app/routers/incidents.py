from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.models import Incident, Platform
from app.routers.common import DbSession, get_or_404
from app.schemas.incident import IncidentCreate, IncidentRead, IncidentSeverity, IncidentStatus, IncidentUpdate

router = APIRouter(prefix='/api/incidents', tags=['incidents'])


@router.post('', response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(data: IncidentCreate, db: DbSession):
    if db.get(Platform, data.platform_id) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, f'Plattform {data.platform_id} existiert nicht')
    incident = Incident(**data.model_dump(), status='open')
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get('', response_model=list[IncidentRead])
def list_incidents(
    db: DbSession,
    platform_id: int | None = None,
    status: IncidentStatus | None = None,
    severity: IncidentSeverity | None = None,
):
    query = select(Incident).order_by(Incident.created_at.desc(), Incident.id.desc())
    if platform_id is not None:
        query = query.where(Incident.platform_id == platform_id)
    if status is not None:
        query = query.where(Incident.status == status)
    if severity is not None:
        query = query.where(Incident.severity == severity)
    return db.scalars(query).all()


@router.get('/{incident_id}', response_model=IncidentRead)
def get_incident(incident_id: int, db: DbSession):
    return get_or_404(db, Incident, incident_id, 'Incident')


@router.put('/{incident_id}', response_model=IncidentRead)
def update_incident(incident_id: int, data: IncidentUpdate, db: DbSession):
    incident = get_or_404(db, Incident, incident_id, 'Incident')
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(incident, field, value)
    # resolved_at folgt automatisch dem Status
    if 'status' in changes:
        if changes['status'] == 'resolved' and incident.resolved_at is None:
            incident.resolved_at = func.now()
        elif changes['status'] != 'resolved':
            incident.resolved_at = None
    db.commit()
    db.refresh(incident)
    return incident
