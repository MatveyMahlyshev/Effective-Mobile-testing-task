from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from api_v1.auth.permissions import check_permission
from core.models import User
from api_v1.rollback import try_commit
from core.models.user import PermissionLevel
from api_v1.auth.auth_helpers import is_used_token


async def get_users(token: str, session: AsyncSession) -> list[User]:
    await is_used_token(token=token, session=session)

    await check_permission(
        token=token,
        session=session,
        permissions=[
            PermissionLevel.ADMIN,
            PermissionLevel.MODERATOR,
        ],
        super_admin=True,
    )
    stmt = select(User).order_by(User.id)
    result = await session.execute(stmt)
    users = result.scalars().all()
    return users


async def get_user_by_id(
    user_id: int,
    token: str,
    session: AsyncSession,
) -> User:
    await is_used_token(token=token, session=session)

    await check_permission(
        token=token,
        session=session,
        permissions=[
            PermissionLevel.ADMIN,
            PermissionLevel.MODERATOR,
        ],
        super_admin=True,
    )
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


async def edit_user_permission(
    user_id: int,
    token: str,
    session: AsyncSession,
    new_permission: int,
) -> User:
    await is_used_token(token=token, session=session)

    await check_permission(
        token=token,
        session=session,
        permissions=[PermissionLevel.ADMIN],
        super_admin=True,
    )

    user = await get_user_by_id(
        user_id=user_id,
        token=token,
        session=session,
    )
    user.permission_level = new_permission
    await try_commit(session=session)
    return user
