from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import http_bearer, get_current_token
from .schemas import UserAuthSchema, TokenInfo
from .auth_helpers import (
    validate_auth_user,
    create_access_token,
    create_refresh_token,
    get_current_auth_user_for_refresh,
    logout_user,
)
from core.models import db_helper

router = APIRouter(
    tags=["Auth"],
    dependencies=[Depends(http_bearer)],
)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenInfo,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Вы неправильно ввели логин или пароль."},
        status.HTTP_404_NOT_FOUND: {"description": "Ваш аккаунт удалён"},
    },
)
async def login_user(
    user: UserAuthSchema = Depends(validate_auth_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):

    access_token = create_access_token(user)
    refresh_token = await create_refresh_token(user=user, session=session)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def auth_refresh(
    user: UserAuthSchema = Depends(get_current_auth_user_for_refresh),
):
    access_token = create_access_token(user=user)
    return TokenInfo(access_token=access_token)


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    token: str = Depends(get_current_token),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await logout_user(token=token, session=session)


# Нужно реализовать добавление аксес токена при логауте, чтобы нельзя было его использовать и там, где берётся этот токен(update, delete), проверять были ли он там.
