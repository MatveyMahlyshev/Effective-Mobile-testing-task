from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.permissions import check_permission
from core.models.user import PermissionLevel


async def get_codes_for_admins_and_moderators(
    token: str,
    session: AsyncSession,
):
    await check_permission(
        token=token,
        session=session,
        permissions=[PermissionLevel.ADMIN, PermissionLevel.MODERATOR],
    )
    return {
        "code_for_admins_and_moderators": "code1",
        "code2_for_admins_and_moderators": "code3",
        "code3_for_admins_and_moderators": "code4",
        "cod4_for_admins_and_moderators": "code5",
    }


async def get_codes_for_admins(
    token: str,
    session: AsyncSession,
):
    await check_permission(
        token=token,
        session=session,
        permissions=[PermissionLevel.ADMIN, PermissionLevel.MODERATOR],
    )
    return {
        "code_for_admins": "code1",
        "code2_for_admins": "code3",
        "code3_for_admins": "code4",
        "cod4_for_admins": "code5",
    }
