from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.dependencies import http_bearer, get_current_token_payload
from core.models import db_helper
from .schemas import UserCreate, UserEdit
from . import crud

main_router = APIRouter(tags=["Users"])
auth_router = APIRouter(dependencies=[Depends(http_bearer)])
router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Электронная почта уже зарегистрирована."},
    },
)
async def register_user(
    user: UserCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_user(user=user, session=session)


@auth_router.put(
    "/update",
    status_code=status.HTTP_200_OK,
    # response_model=UserEditCreate,
)
async def update_user(
    user: UserEdit,
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.update_user(user=user, payload=payload, session=session)


@router.delete(
    "/delete",
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_user():
    pass


main_router.include_router(router)
main_router.include_router(auth_router)
