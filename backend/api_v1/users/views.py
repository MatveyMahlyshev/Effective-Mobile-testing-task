from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper
from .schemas import UserCreate
from . import crud

router = APIRouter(tags=["Users"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_user(user=user, session=session)
