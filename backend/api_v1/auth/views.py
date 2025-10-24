from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import get_tokens
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
def login_user(
    response: Response,
    user: UserAuthSchema = Depends(validate_auth_user),
):
    """
    Генерация access и refresh, и сохранение в cookies при логине.
    Небезопасно, но для примера сойдёт.
    """

    access_token = create_access_token(user=user, response=response)
    refresh_token = create_refresh_token(user=user, response=response)
    
    
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Вы не авторизованы."}},
)
async def auth_refresh(
    response: Response,
    user: UserAuthSchema = Depends(get_current_auth_user_for_refresh),
):
    """
    Получение нового access токена по refresh токену
    """
    access_token = create_access_token(user=user, response=response)
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
    При логауте access и refresh токены отправляются в список использованных.
    """
    return await logout_user(
        access_token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        session=session,
        response=response,
    )
