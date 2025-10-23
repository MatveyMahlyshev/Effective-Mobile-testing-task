from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Form, status, HTTPException
from sqlalchemy import select, Result
from typing import Annotated
from pydantic import EmailStr
from datetime import timedelta
from core.config import settings
import time


from core.models import db_helper, User, Token
from .pwd import validate_password
from .schemas import UserAuthSchema
from . import dependencies
from .token import decode_jwt


async def check_token_revoked(
    token: str = Depends(dependencies.get_current_token),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    stmt = select(Token).where(Token.token == token)
    result = await session.execute(stmt)
    revoked_token = result.scalar()
    if revoked_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Войдите снова."
        )
    return token


def is_active(user: User):
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ваш аккаунт удалён.",
        )


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
            detail="Вы неправильно ввели почту или пароль.",
        )
    is_active(user=user)

    return user


def create_access_token(user: UserAuthSchema) -> str:
    jwt_payload = {
        "sub": user.email,
    }
    return dependencies.create_token(
        token_type=dependencies.TokenTypeFields.ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
    )


async def create_refresh_token(user: UserAuthSchema, session: AsyncSession) -> str:
    jwt_payload = {"sub": user.email}
    token = dependencies.create_token(
        token_type=dependencies.TokenTypeFields.REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth.refresh_token_expire_days)
    )
    return token

async def get_user_by_token_sub(payload: dict, session: AsyncSession) -> User:
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильно введены логин или пароль",
        )
    return user


async def get_current_auth_user_for_refresh(
    token: str = Depends(dependencies.get_current_token),
    payload: dict = Depends(dependencies.get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserAuthSchema:

    if int(decode_jwt(token).get("exp")) - int(time.time()) <= 0:
        await logout_user(token=token, session=session)

    dependencies.validate_token_type(
        payload=payload, token_type=dependencies.TokenTypeFields.REFRESH_TOKEN_TYPE
    )
    return await get_user_by_token_sub(payload=payload, session=session)


async def logout_user(token: str, session: AsyncSession):
    session.add(Token(token=token))
    await session.commit()
    return {"message": "Success logout."}
