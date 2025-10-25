from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Form, status, HTTPException, Request, Response
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
from api_v1.rollback import try_commit


async def is_used_token(token: str, session: AsyncSession):
    token_exists = await session.execute(select(Token).where(Token.token == token))
    if token_exists.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильынй токен.",
        )


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


def create_access_token(user: UserAuthSchema, response: Response) -> str:
    jwt_payload = {
        "sub": user.email,
    }
    token = dependencies.create_token(
        token_type=dependencies.TokenTypeFields.ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 24 * 60 * 60,
        path="/",
    )
    return token


def create_refresh_token(user: UserAuthSchema, response: Response):
    jwt_payload = {"sub": user.email}
    token = dependencies.create_token(
        token_type=dependencies.TokenTypeFields.REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth.refresh_token_expire_days),
    )
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 24 * 60 * 60,
        path="/",
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
    request: Request,
    response: Response,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserAuthSchema:

    refresh_token = request.cookies.get("refresh_token")
    access_token = request.cookies.get("access_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы для данного действия",
        )

    if int(decode_jwt(refresh_token).get("exp")) - int(time.time()) <= 0:
        await logout_user(
            access_token=access_token,
            refresh_token=refresh_token,
            session=session,
            response=response,
        )
    response.delete_cookie("access_token")
    session.add(Token(token=access_token))
    await try_commit(session=session)

    payload = dependencies.get_current_token_payload(refresh_token)

    dependencies.validate_token_type(
        payload=payload, token_type=dependencies.TokenTypeFields.REFRESH_TOKEN_TYPE
    )
    return await get_user_by_token_sub(payload=payload, session=session)


async def logout_user(
    access_token: str,
    refresh_token: str,
    session: AsyncSession,
    response: Response,
):

    if not (access_token and refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Чтобы выйти из системы, нужно сначала зайти.",
        )

    session.add(Token(token=access_token))
    session.add(Token(token=refresh_token))
    response.delete_cookie("refresh_token")
    response.delete_cookie("access_token")
    await try_commit(session=session)
    return {"message": "Success logout."}
