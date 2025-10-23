from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Form, status, HTTPException
from sqlalchemy import select, Result
from typing import Annotated
from pydantic import EmailStr


from core.models import db_helper, User
from .pwd import validate_password
from .schemas import UserAuthSchema
from . import dependencies


async def validate_auth_user(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form()],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):

    stmt = select(User).where(User.email == email)
    result: Result = await session.execute(statement=stmt)
    user: User = result.scalar()
    if not user or not validate_password(password=password, hashed_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы неправильно ввели логин или пароль.",
        )

    return user


def create_access_token(user: UserAuthSchema) -> str:
    jwt_payload = {
        "sub": user.email,
    }
    return dependencies.create_token(
        token_type=dependencies.TokenTypeFields.ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
    )


def create_refresh_token(user: UserAuthSchema) -> str:
    jwt_payload = {"sub": user.email}
    return dependencies.create_token(
        token_type=dependencies.TokenTypeFields.REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
    )


async def get_user_by_token_sub(payload: dict, session: AsyncSession) -> UserAuthSchema:
    email: str | None = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
        )

    stmt = select(User).where(User.email == email)
    result: Result = await session.execute(statement=stmt)
    user: User = result.scalar()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильно введены логин или пароль",)
    return user


async def get_current_auth_user_for_refresh(
    payload: dict = Depends(dependencies.get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserAuthSchema:
    dependencies.validate_token_type(
        payload=payload, token_type=dependencies.TokenTypeFields.REFRESH_TOKEN_TYPE
    )
    return await get_user_by_token_sub(payload=payload, session=session)
