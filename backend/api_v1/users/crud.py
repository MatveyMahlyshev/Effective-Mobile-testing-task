from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from .schemas import UserCreate
from core.models import User
from api_v1.auth.pwd import hash_password


async def create_user(user: UserCreate, session: AsyncSession):
    email_exists = await session.execute(select(User).where(User.email == user.email))
    if email_exists.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Электронная почта уже зарегистрирована.",
        )
    new_user = User(
        email=user.email,
        last_name=user.last_name,
        first_name=user.first_name,
        patronymic=user.patronymic,
        password=hash_password(user.password),
        is_active=True,
        is_superuser=False,
    )
    session.add(new_user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Электронная почта уже зарегистрирована.",
        )
    return new_user
