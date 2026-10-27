from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Platform
from app.schemas.platform import Environment, PlatformCreate, PlatformRead, PlatformUpdate

router = APIRouter(prefix='/api/platforms', tags=['platforms'])

DbSession = Annotated[Session, Depends(get_db)]


def get_platform_or_404(db: Session, platform_id: int) -> Platform:
    platform = db.get(Platform, platform_id)
    if platform is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Plattform nicht gefunden')
    return platform


def commit_or_409(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, 'Eine Plattform mit diesem Namen existiert bereits')


@router.post('', response_model=PlatformRead, status_code=status.HTTP_201_CREATED)
def create_platform(data: PlatformCreate, db: DbSession):
    platform = Platform(**data.model_dump())
    db.add(platform)
    commit_or_409(db)
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
    return get_platform_or_404(db, platform_id)


@router.put('/{platform_id}', response_model=PlatformRead)
def update_platform(platform_id: int, data: PlatformUpdate, db: DbSession):
    platform = get_platform_or_404(db, platform_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(platform, field, value)
    commit_or_409(db)
    db.refresh(platform)
    return platform


@router.delete('/{platform_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_platform(platform_id: int, db: DbSession):
    platform = get_platform_or_404(db, platform_id)
    db.delete(platform)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
