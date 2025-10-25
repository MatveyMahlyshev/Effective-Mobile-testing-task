from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.dependencies import get_tokens
from api_v1.users.schemas import UserGet
from core.models import db_helper
from . import crud
from .schemas import EditPermission

router = APIRouter(tags=["Admin"])


@router.get("/users/list", response_model=list[UserGet])
async def get_users(
    tokens: dict = Depends(get_tokens),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Получение списка пользователей. Обычный пользователь не может его получить. Только админ или модератор.
    """
    return await crud.get_users(token=tokens.get("access_token"), session=session)


@router.get("/users/{user_id}", response_model=UserGet)
async def get_user_by_id(
    user_id: int,
    tokens: dict = Depends(get_tokens),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Получение пользователя по id. Только для админа и модератора.
    """
    return await crud.get_user_by_id(
        user_id=user_id, token=tokens.get("access_token"), session=session
    )


@router.patch("/edit_permission/{user_id}", response_model=UserGet)
async def edit_user_permission(
    permission: EditPermission,
    user_id: int,
    tokens: dict = Depends(get_tokens),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Изменение уровня доступа для пользователя.
    Только для админа высшего уровня, которого permission_level == 3 и is_superuser == True.
    """
    return await crud.edit_user_permission(
        user_id=user_id,
        token=tokens.get("access_token"),
        session=session,
        new_permission=permission.permission,
    )
