from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import Base, get_db

DbSession = Annotated[Session, Depends(get_db)]


def get_or_404[M: Base](db: Session, model: type[M], object_id: int, label: str) -> M:
    obj = db.get(model, object_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'{label} nicht gefunden')
    return obj


def commit_or_409(db: Session, message: str) -> None:
    """Speichert; verletzt das eine Unique-Regel (z. B. doppelter Name), gibt es 409."""
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, message)
