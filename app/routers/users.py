from fastapi import APIRouter, Response, status
from sqlalchemy import select

from app.models import User
from app.routers.common import DbSession, commit_or_409, get_or_404
from app.schemas.user import UserCreate, UserRead, UserRole, UserUpdate

router = APIRouter(prefix='/api/users', tags=['users'])

EMAIL_TAKEN = 'Ein User mit dieser E-Mail-Adresse existiert bereits'


@router.post('', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: DbSession):
    user = User(**data.model_dump())
    db.add(user)
    commit_or_409(db, EMAIL_TAKEN)
    db.refresh(user)
    return user


@router.get('', response_model=list[UserRead])
def list_users(db: DbSession, role: UserRole | None = None, include_inactive: bool = False):
    query = select(User).order_by(User.id)
    if role is not None:
        query = query.where(User.role == role)
    if not include_inactive:
        query = query.where(User.is_active)
    return db.scalars(query).all()


@router.get('/{user_id}', response_model=UserRead)
def get_user(user_id: int, db: DbSession):
    return get_or_404(db, User, user_id, 'User')


@router.put('/{user_id}', response_model=UserRead)
def update_user(user_id: int, data: UserUpdate, db: DbSession):
    user = get_or_404(db, User, user_id, 'User')
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    commit_or_409(db, EMAIL_TAKEN)
    db.refresh(user)
    return user


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(user_id: int, db: DbSession):
    """Deaktiviert den User. Die Zeile bleibt, weil Deployments und Chats auf sie verweisen."""
    user = get_or_404(db, User, user_id, 'User')
    user.is_active = False
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
