from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import UserCreate


async def create_user(user: UserCreate, session: AsyncSession):
    pass
