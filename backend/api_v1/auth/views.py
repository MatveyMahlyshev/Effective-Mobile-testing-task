from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import http_bearer, get_tokens
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
    response: Response,
    user: UserAuthSchema = Depends(validate_auth_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Генерация access и refresh, и сохранение в cookies при логине.
    Небезопасно, но для примера сойдёт.
    """

    access_token = create_access_token(user)
    refresh_token = await create_refresh_token(user=user, session=session)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 24 * 60 * 60,
        path="/",
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 24 * 60 * 60,
        path="/",
    )
    return TokenInfo(
        access_token=access_token,
    )


@router.post(
    "/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Вы не авторизованы."}}
)
async def auth_refresh(
    user: UserAuthSchema = Depends(get_current_auth_user_for_refresh),
):
    """
    Получение нового access токена по refresh токену
    """
    access_token = create_access_token(user=user)
    return TokenInfo(access_token=access_token)


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    response: Response,
    token: dict = Depends(get_tokens),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    При логауте старый access токен отправляется в список использованных токенов.
    По идее refresh токен таким же образом должен попасть в blacklist.
    """
    return await logout_user(
        access_token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        session=session,
        response=response,
    )


# Нужно реализовать добавление аксcес токена при логауте, чтобы нельзя было его использовать и там, где берётся этот токен(update, delete), проверять были ли он там.
