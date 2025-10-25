from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from api_v1.auth.auth_helpers import get_user_by_token_sub
from api_v1.auth.dependencies import get_current_token_payload


async def check_permission(token: str, session: AsyncSession, permissions: list[int]):
    payload: dict = get_current_token_payload(token)

    user = await get_user_by_token_sub(payload=payload, session=session)
    if not user.permission_level in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к данному ресурсу",
        )
