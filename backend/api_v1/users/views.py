from fastapi import APIRouter, status, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.dependencies import get_tokens
from api_v1.auth.auth_helpers import logout_user
from core.models import db_helper
from .schemas import UserCreate, UserEdit
from . import crud

main_router = APIRouter()
router = APIRouter(tags=["Users"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Электронная почта уже зарегистрирована."
        },
    },
)
async def register_user(
    user: UserCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Регистрация пользователя.
    """

    return await crud.create_user(
        user=user,
        session=session,
    )


@router.put(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=UserEdit,
)
async def update_user(
    user: UserEdit,
    tokens: dict = Depends(get_tokens),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Обновление данных пользователя. В данном случае ФИО.
    """
    return await crud.update_user(
        user=user,
        token=tokens.get("access_token"),
        session=session,
    )


@router.delete(
    "/delete",
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_user(
    response: Response,
    tokens: dict = Depends(get_tokens),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Мягкое удаление пользователя(флаг is_active становится false) и logout.
    """
    await crud.delete_user(
        token=tokens.get("access_token"),
        session=session,
    )
    return await logout_user(
        access_token=tokens.get("access_token"),
        refresh_token=tokens.get("refresh_token"),
        session=session,
        response=response,
    )
