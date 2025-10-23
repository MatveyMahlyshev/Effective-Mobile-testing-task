from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper
from .schemas import UserCreate
from . import crud

router = APIRouter(tags=["Users"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Электронная почта уже зарегистрирована."},
    },
)
async def register_user(
    user: UserCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_user(user=user, session=session)


@router.put(
    "/update",
    status_code=status.HTTP_200_OK,
)
async def update_user():
    pass


@router.delete(
    "/delete",
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_user():
    pass
