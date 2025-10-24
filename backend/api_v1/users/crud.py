from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


from .schemas import UserCreate, UserEdit
from core.models import User
from api_v1.auth.pwd import hash_password
from api_v1.auth.auth_helpers import get_user_by_token_sub, is_active, is_used_token
from api_v1.auth.dependencies import get_current_token_payload, validate_token_type, TokenTypeFields


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


async def update_user(user: UserEdit, token: str, session: AsyncSession):
    await is_used_token(token=token, session=session)
    payload = get_current_token_payload(token=token)
    validate_token_type(payload=payload, token_type=TokenTypeFields.ACCESS_TOKEN_TYPE)

    old_user = await get_user_by_token_sub(payload=payload, session=session)

    is_active(old_user)
    old_user.first_name = user.first_name
    old_user.last_name = user.last_name
    old_user.patronymic = user.patronymic

    await session.commit()
    return old_user


async def delete_user(token: str, session: AsyncSession):
    await is_used_token(token=token, session=session)
    payload = get_current_token_payload(token=token)
    validate_token_type(payload=payload, token_type=TokenTypeFields.ACCESS_TOKEN_TYPE)
    old_user = await get_user_by_token_sub(payload=payload, session=session)
    is_active(old_user)
    old_user.is_active = False
    await session.commit()
    return old_user
