from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.dependencies import get_tokens
from . import crud
from core.models import db_helper

router = APIRouter(tags=["MOCK-VIEWS"])


@router.get("/codes/open", status_code=status.HTTP_200_OK)
def get_codes_for_all_users():
    codes = {
        "code_for_all": "code1",
        "code2_for_all": "code3",
        "code3_for_all": "code4",
        "cod4_for_all": "code5",
    }
    """Простейшая view. Данные может получить любой пользователь"""
    return codes

@router.get("/codes/secret/for/admins/and/moderators", status_code=status.HTTP_200_OK)
async def get_codes_for_admins_and_moderators(tokens: dict = Depends(get_tokens), session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    """View c проверкой на то, является ли пользователь админом или модератором"""
    return await crud.get_codes_for_admins_and_moderators(token=tokens.get("access_token"), session=session)

@router.get("/codes/secret/for/admins/only", status_code=status.HTTP_200_OK)
async def get_codes_for_admins_and_moderators(tokens: dict = Depends(get_tokens), session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    """View c проверкой на то, является ли пользователь админом"""
    return await crud.get_codes_for_admins(token=tokens.get("access_token"), session=session)
