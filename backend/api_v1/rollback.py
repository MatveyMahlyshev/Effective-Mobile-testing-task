from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status as sc
from sqlalchemy.exc import IntegrityError


async def try_commit(
    session: AsyncSession,
    status: int | None = sc.HTTP_500_INTERNAL_SERVER_ERROR,
    text: str | None = "Integrity error.",
):
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status,
            detail=text,
        )
