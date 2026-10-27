from fastapi import APIRouter, Response, status
from sqlalchemy import select

from app.models import Platform
from app.routers.common import DbSession, commit_or_409, get_or_404
from app.schemas.platform import Environment, PlatformCreate, PlatformRead, PlatformUpdate

router = APIRouter(prefix='/api/platforms', tags=['platforms'])

NAME_TAKEN = 'Eine Plattform mit diesem Namen existiert bereits'


@router.post('', response_model=PlatformRead, status_code=status.HTTP_201_CREATED)
def create_platform(data: PlatformCreate, db: DbSession):
    platform = Platform(**data.model_dump())
    db.add(platform)
    commit_or_409(db, NAME_TAKEN)
    db.refresh(platform)
    return platform


@router.get('', response_model=list[PlatformRead])
def list_platforms(db: DbSession, environment: Environment | None = None):
    query = select(Platform).order_by(Platform.id)
    if environment is not None:
        query = query.where(Platform.environment == environment)
    return db.scalars(query).all()


@router.get('/{platform_id}', response_model=PlatformRead)
def get_platform(platform_id: int, db: DbSession):
    return get_or_404(db, Platform, platform_id, 'Plattform')


@router.put('/{platform_id}', response_model=PlatformRead)
def update_platform(platform_id: int, data: PlatformUpdate, db: DbSession):
    platform = get_or_404(db, Platform, platform_id, 'Plattform')
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(platform, field, value)
    commit_or_409(db, NAME_TAKEN)
    db.refresh(platform)
    return platform


@router.delete('/{platform_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_platform(platform_id: int, db: DbSession):
    platform = get_or_404(db, Platform, platform_id, 'Plattform')
    db.delete(platform)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
